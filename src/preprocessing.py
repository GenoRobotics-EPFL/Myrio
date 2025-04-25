import asyncio as aio
import os
from pathlib import Path
from types import NoneType

import polars as pl
from Bio import SeqIO
from safe_result import Err, Ok, Result, safe_async

import utils


def read_check(input_fastq: Path, threshold: int = 10) -> Result[NoneType, ValueError]:
    """
    Check if the FASTQ file has enough reads.
    """
    n = 0
    for _ in SeqIO.parse(input_fastq, "fastq"):
        n += 1
        if n >= threshold:
            return Ok(None)

    return Err(ValueError(f"FASTQ file contains `{n}` reads, expected `>{threshold}` reads."))


async def run_seqkit(
    input_filepath: Path, output_filepath: Path, min_len: int = 150, min_qual: int = 10, max_qual: int = 60
) -> Result[NoneType, Exception]:
    """Filtering with SeqKit."""
    # fmt: off
    command = [
        "seqkit", "seq",
        "-Q", str(min_qual),   # Minimum quality
        "-R", str(max_qual),   # Maximum quality
        "-m", str(min_len),    # Minimum sequence length
        str(input_filepath),
        "-o", str(output_filepath)
    ]
    # fmt: on
    results = await utils.exec_command(command)
    return results


async def run_nanoplot(input_fastq: Path, output_dir: Path) -> Result[NoneType, Exception]:
    """Runs NanoPlot to generate quality and length distribution graphs from a FASTQ file.

    Parameters:
        input_fastq (Path): Path to the FASTQ file.
        output_dir (Path): Directory where NanoPlot outputs will be saved.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # fmt: off
    command = [
        "NanoPlot",
        "--fastq", str(input_fastq),
        "--outdir", str(output_dir),
        "--verbose",
        "--N50",
        "--plots", "kde",  # or all
        "--loglength",
    ]
    # fmt: on
    results = await utils.exec_command(command)
    return results


@safe_async
async def preprocessing(input_fastq: Path, output_fastq: Path) -> None:
    read_check(input_fastq).unwrap()
    (await run_seqkit(input_fastq, output_fastq)).unwrap()


async def main():
    data_df = utils.load_data_df()
    species = "Allium_Ursinum"
    marker = utils.Markers.ITS

    output_base = Path(f"output/{species}/")
    output_nanoplot = Path(output_base, "nanoplot/")
    os.makedirs(output_nanoplot, exist_ok=True)
    output_filtered_reads = Path(output_base, "filtered_reads.fastq")

    fastq = (
        data_df.filter((pl.col("name") == species) & (pl.col(marker.value) == True) & (pl.col("reference") == False))  # noqa: E712
        .select("filepath")
        .item()
    )

    fastq = Path(fastq)

    # visualization and preprocessing
    (await run_nanoplot(fastq, output_dir=output_nanoplot)).unwrap()
    await preprocessing(fastq, output_filtered_reads)
    (await run_nanoplot(output_filtered_reads, output_dir=output_nanoplot)).unwrap()


if __name__ == "__main__":
    aio.run(main())
