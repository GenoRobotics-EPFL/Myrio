import asyncio as aio
import dataclasses
from os import PathLike
from pathlib import Path

import aiofiles as aiof
import numpy as np
import polars as pl
from safe_result import Err, Ok, Result

import utils


@dataclasses.dataclass
class Raxtax:
    df: pl.DataFrame

    @staticmethod
    def get_row_schema() -> list[str]:
        return [
            "phyllum",
            "phyllum_score",
            "class",
            "class_score",
            "order",
            "order_score",
            "family",
            "family_score",
            "genus",
            "genus_score",
            "species",
            "species_score",
            "local_confidence_score",  # from raxtax: the confidence in the reported lineage (local signal)
            "global_confidence_score",  # from raxtax: confidence in the confidence values themselves on sequence level (global signal)
        ]

    @staticmethod
    async def build(input: str | PathLike, db: str | PathLike) -> Result["Raxtax", RuntimeError]:
        """Builds the Raxtax class by executing raxtab in a subprocess and parsing its results.

        Args:
            input (str | PathLike): The query fasta filepath.
            db (str | PathLike): The reference fasta/bin filepath.

        Returns:
            A result containing the RaxtaxResult if successfull.
        """
        if not utils.check_filepath(input, readable=True):
            return Err(RuntimeError("Input filepath is invalid."))
        if not utils.check_filepath(db, readable=True):
            return Err(RuntimeError("DB filepath is invalid."))

        raxtax_output = None
        async with aiof.tempfile.TemporaryDirectory(prefix="raxtax_") as dir:
            proc = await aio.subprocess.create_subprocess_exec(
                "raxtax",
                "--query-file",
                f"{input}",
                "--database-path",
                f"{db}",
                "--prefix",
                dir,
                "--quiet",
                "--redo",
                "--tsv",  # Raxtax .tsv output is easier to parse
                stdin=None,
                stdout=None,
                stderr=aio.subprocess.PIPE,
            )

            _, stderr = await proc.communicate()
            if stderr:
                print(f"[raxtax stderr]\n{stderr.decode()}\n")

            output_filepath = Path(dir, "raxtax.tsv")
            if not output_filepath.exists():
                return Err(RuntimeError(f"Raxtax seems to have failed, `{output_filepath}` does not exist"))

            async with aiof.open(output_filepath, "r") as output_file:
                raxtax_output = await output_file.readlines()

        # this is pretty hacky, unsafe even, this requires sequences in the fasta database to look something like the following.
        # >BOLD_PID=CAATB198-11|MARKER_CODE=rbcL;tax=phylum:Tracheophyta,class:Magnoliopsida,order:Fabales,family:Fabaceae,genus:Bauhinia,species:Bauhinia_cheilantha;
        # NNNNNNNNNNNNCAAAC...

        parsed_raxtax_output = []
        for line in raxtax_output:
            line = line.split("\t")[1:-1]

            line[0] = line[0][7:]  # removes "phylum:" prefix
            line[2] = line[2][6:]  # class
            line[4] = line[4][6:]  # order
            line[6] = line[6][7:]  # family
            line[8] = line[8][6:]  # genus
            line[10] = line[10][8:]  # species

            parsed_raxtax_output.append(np.array(line))

        return Ok(Raxtax(pl.DataFrame(parsed_raxtax_output, schema=Raxtax.get_row_schema(), orient="row")))


if __name__ == "__main__":
    match aio.run(Raxtax.build("ignore/figus_matK.fasta", "ignore/Magnoliopsida_matK_raxdb.fasta")):
        case Ok(val):
            print(val)
        case Err(error):
            print(error)
