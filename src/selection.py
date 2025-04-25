import asyncio as aio
import os
from pathlib import Path
from types import NoneType

from safe_result import Result, safe_async

import utils


@safe_async
async def run_isONclust3(
    fastq_fp: Path, output_dir: Path, post_cluster_flag: bool = True, n_flag: int = 3
) -> list[Path]:
    """Runs isONclust3 on the provided `fastq_file`.

    Args:
        ...
        post_cluster_flag (bool): If set to true, run the post clustering step during the analysis (small improvement for results but much higher runtime)
        n_flag (int): Minimum number of reads for cluster.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # fmt: off
    command = [
        "isONclust3",
        "--fastq", str(fastq_fp),
        "--outfolder", str(output_dir),
        "--mode", "ont",
        "--n", str(n_flag)
    ]
    # fmt: on
    if post_cluster_flag:
        command.append("--post-cluster")

    (await utils.exec_command(command)).unwrap()

    path = Path(output_dir, "clustering", "fastq_files")
    if not path.exists():
        raise RuntimeError(f"Expected the path `{path}` to exist as the command doesn't seem to have failed.")

    filepaths: list[Path] = []
    for root, _, files in path.walk():
        for file in files:
            filepath = Path(root, file)
            if filepath.suffix == ".fastq":
                filepaths.append(filepath)

    return filepaths


# Cleaning for contaminations (selecting only clusters corresponding to angiosperms)
async def run_blastn(
    query_file: Path, db_path: Path, output_file: Path, evalue: float = 1e-5, outfmt: int = 6
) -> Result[NoneType, Exception]:
    """
    Runs BLASTN on a given query file against a specified database.

    Args:
        query_file (str): Path to the FASTA file with the query sequence(s).
        db_path (str): Path to the BLAST database (excluding file extensions).
        output_file (str): Path to save the BLAST output.
        evalue (float): E-value threshold for saving hits (default: 1e-5).
        outfmt (int): BLAST output format (default: 6 = tabular).
    """
    # fmt: off
    command = [
        "blastn",
        "-query", str(query_file),
        "-db", str(db_path),
        "-out", str(output_file),
        "-evalue", str(evalue),
        "-outfmt", str(outfmt),
    ]
    # fmt: on

    results = await utils.exec_command(command)
    return results


async def main():
    species = "Allium_Ursinum"
    marker = utils.Markers.ITS

    output_base = Path(f"output/{species}/")
    filtered_reads = Path(output_base, "filtered_reads.fastq")
    output_cluster = output_base  # isONclust3 creates `cluster` path on its own
    output_dir = Path(output_base, "cluster_output/BLAST")  # okutput directory for BLAST results
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run isONclust3 clustering
    cluster_filepaths = (await run_isONclust3(filtered_reads, output_cluster)).unwrap()
    print(cluster_filepaths)

    # Decontamination (Cleaning for contaminations (selecting only clusters corresponding to angiosperms)
    for file in cluster_filepaths:
        # Convert .fastaq or .fastq to .fasta
        fasta_file = file.with_suffix(".fasta")
        fasta_file = utils.convert_fastq_to_fasta(file, fasta_file)

        # Define output file path
        output_file = Path(output_dir, f"{fasta_file.stem}_blast.out")

        # Run BLASTN
        (await run_blastn(fasta_file, Path("database/"), output_file)).unwrap()

    # deleting all non plant clusters (empty files)
    # delete_empty_files("cluster_output/BLAST", recursive=True)


if __name__ == "__main__":
    aio.run(main())
