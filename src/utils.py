import re
from os import R_OK, W_OK, PathLike, access
from pathlib import Path

import polars as pl


def check_filepath(filepath: str | PathLike, readable: bool = False, writeable: bool = False) -> bool:
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


def __gen_data_helper_csv():
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
