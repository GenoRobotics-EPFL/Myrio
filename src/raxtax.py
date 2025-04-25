import dataclasses
from pathlib import Path

import aiofiles as aiof
import numpy as np
import polars as pl
from safe_result import Err, Ok, Result, safe

import utils


@dataclasses.dataclass
class Raxtax:
    df: pl.DataFrame

    @staticmethod
    def get_row_schema() -> list[str]:
        return [
            "phylum",
            "phylum_score",
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
    @safe
    async def build(input_fp: Path, db_fp: Path, output_dir: Path) -> Result["Raxtax", Exception]:
        """Builds the Raxtax class by executing raxtab in a subprocess and parsing its results.

        Args:
            input (str | PathLike): The query fasta filepath.
            db (str | PathLike): The reference fasta/bin filepath.

        Returns:
            A result containing the RaxtaxResult if successfull.
        """

        raxtax_output = None
        # fmt: off
        command = [
            "raxtax",
            "--query-file", str(input_fp),
            "--database-path", str(db_fp),
            "--prefix", str(output_dir),
            "--quiet",
            "--redo",
            "--tsv",  # Raxtax .tsv output is much easier to parse
        ]
        # fmt: on
        (await utils.exec_command(command)).unwrap()

        output_fp = Path(output_dir, "raxtax.tsv")
        if not output_fp.exists():
            return Err(RuntimeError(f"Raxtax seems to have failed, `{output_fp}` does not exist"))
        async with aiof.open(output_fp, "r") as output_file:
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

        df = (
            pl.DataFrame(parsed_raxtax_output, schema=Raxtax.get_row_schema(), orient="row")
            .with_columns(
                pl.col("phylum_score").cast(pl.Float64),
                pl.col("class_score").cast(pl.Float64),
                pl.col("order_score").cast(pl.Float64),
                pl.col("family_score").cast(pl.Float64),
                pl.col("genus_score").cast(pl.Float64),
                pl.col("species_score").cast(pl.Float64),
                pl.col("local_confidence_score").cast(pl.Float64),
                pl.col("global_confidence_score").cast(pl.Float64),
            )
            .sort(
                by="species_score",
            )
        )
        return Ok(Raxtax(df))


if __name__ == "__main__":
    pass
