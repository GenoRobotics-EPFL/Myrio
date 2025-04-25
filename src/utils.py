import asyncio as aio
import re
from enum import Enum
from os import R_OK, W_OK, PathLike, access
from pathlib import Path
from typing import Any

import polars as pl
from Bio import SeqIO
from safe_result import Err, Ok, Result


class Markers(Enum):
    matK = "matK"
    rbcL = "rbcL"
    psbA_trnH = "psbA-trnH"
    ITS = "ITS"

    @staticmethod
    def all() -> list["Markers"]:
        return [Markers.matK, Markers.rbcL, Markers.psbA_trnH, Markers.ITS]


def convert_fastq_to_fasta(
    input_filepath: str | PathLike[Any], output_filepath: str | PathLike[Any], debug: bool = False
) -> Path:
    """Converts a FASTQ file to FASTA format using Biopython.

    Returns:
        The output filepath for convenience.
    """
    input_filepath = Path(input_filepath)
    output_filepath = Path(output_filepath)

    count = SeqIO.convert(input_filepath, "fastq", output_filepath, "fasta")
    print(f"Converted {count} records from {input_filepath} to {output_filepath}") if debug else ()
    return output_filepath


def check_filepath(filepath: str | PathLike[Any], readable: bool = False, writeable: bool = False) -> bool:
    """Checks if a file exists and more.

    Args:
        filepath (str | PathLike): The filepath to check.
        readable (bool, optional): Also checks that the file can be read. Defaults to False.
        writeable (bool, optional): Also checks that the file can be written to. Defaults to False.

    Returns:
        bool: The result represented by a boolean.
    """
    filepath = Path(filepath)
    read_check = access(filepath, R_OK) if readable else True
    write_check = access(filepath, W_OK) if readable else True

    return filepath.is_file() and read_check and write_check


def load_data_df() -> pl.DataFrame:
    """Returns a helper dataframe to manage the data files.

    ┌─────────────────┬───────────┬───────┬───────┬───────────┬───────┬─────────────────────────────────┐
    │ name            ┆ reference ┆ matk  ┆ rbcL  ┆ psbA-trnH ┆ ITS   ┆ filepath                        │
    │ ---             ┆ ---       ┆ ---   ┆ ---   ┆ ---       ┆ ---   ┆ ---                             │
    │ str             ┆ bool      ┆ bool  ┆ bool  ┆ bool      ┆ bool  ┆ str                             │
    ╞═════════════════╪═══════════╪═══════╪═══════╪═══════════╪═══════╪═════════════════════════════════╡
    │ Allium_Ursinum  ┆ false     ┆ false ┆ false ┆ false     ┆ true  ┆ data/expedition_jardin_botaniq… │
    │ Ficus_religiosa ┆ false     ┆ false ┆ false ┆ false     ┆ true  ┆ data/expedition_jardin_botaniq… │
    │ Ficus_religiosa ┆ true      ┆ false ┆ false ┆ false     ┆ true  ┆ data/expedition_jardin_botaniq… │
    │ …               ┆ …         ┆ …     ┆ …     ┆ …         ┆ …     ┆ …                               │
    │ Viburnum_opulus ┆ false     ┆ true  ┆ true  ┆ true      ┆ true  ┆ data/summer_expedition/Viburnu… │
    │ Tomato          ┆ false     ┆ false ┆ true  ┆ false     ┆ false ┆ data/tomato/rbcL_Qiagen_tomato… │
    └─────────────────┴───────────┴───────┴───────┴───────────┴───────┴─────────────────────────────────┘
    """
    return pl.read_csv("data.csv")


async def exec_command(command: list[str]) -> Result[None, RuntimeError]:
    try:
        proc = await aio.create_subprocess_exec(*command, stdout=aio.subprocess.DEVNULL, stderr=aio.subprocess.PIPE)
    except FileNotFoundError as e:
        return Err(RuntimeError(f"Command not found: {command[0]}"))
    except OSError as error:
        return Err(RuntimeError(f"Failed to start command `{command}`: {error}"))
    except Exception as error:
        return Err(RuntimeError(f"Unexpected error while starting command `{command}`: {error}"))

    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        stderr = stderr.decode(encoding="utf-8", errors="ignore")
        return Err(RuntimeError(f"Command failed with exit code `{proc.returncode}`\n{stderr}"))

    return Ok(None)


def _gen_data_helper_csv():
    reference_re = re.compile(r"reference")
    matk_re = re.compile("[mM][aA][tT][kK]")
    rbcl_re = re.compile(r"[rR][bB][cC][lL]")
    psba_trnh_re = re.compile(r"([pP][sS][bB][aA]-[tT][rR][nN][hH])|([tT][rR][nN][hH]-[pP][sS][bB][aA])")
    its_re = re.compile(r"[iI][tT][sS]")
    name_re = re.compile(r"[A-Za-z]+_[A-Za-z]+")

    output = []
    for root, dirs, files in Path("./data/").walk():
        for file in files:
            filepath = Path(root, file)
            filename_str = str(file)
            filepath_str = str(filepath)

            if ".fastq" not in filename_str and ".fasta" not in filename_str:
                continue

            name = "Unknown"
            name_match = name_re.search(filename_str)
            if name_match is not None:
                name = name_match[0]

            output.append(
                {
                    "name": name,
                    "reference": True if reference_re.search(filename_str) is not None else False,
                    "matk": True if matk_re.search(filepath_str) is not None else False,
                    "rbcL": True if rbcl_re.search(filepath_str) is not None else False,
                    "psbA-trnH": True if psba_trnh_re.search(filepath_str) is not None else False,
                    "ITS": True if its_re.search(filepath_str) is not None else False,
                    "filepath": str(filepath),
                }
            )

    df = pl.DataFrame(output)
    df.write_csv("data_unchecked.csv")  # some names have to be fixed manually


if __name__ == "__main__":
    pass
