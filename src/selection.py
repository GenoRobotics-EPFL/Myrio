import os
from pathlib import Path

from safe_result import Err, Ok, Result, ok

import utils


async def run_isONclust3(
    fastq_file: Path, output_folder: Path, post_cluster_flag: bool = True, n_flag: int = 3
) -> Result[list[Path], RuntimeError]:
    """Runs isONclust3 on the provided `fastq_file`.

    Args:
        ...
        post_cluster_flag (bool): If set to true, run the post clustering step during the analysis (small improvement for results but much higher runtime)
        n_flag (int): Minimum number of reads for cluster.
    """
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # fmt: off
    command = [
        "isONclust3",
        "--fastq", str(fastq_file),
        "--outfolder", str(output_folder),
        "--mode", "ont",
        "--n", str(n_flag)
    ]
    # fmt: on
    if post_cluster_flag:
        command.append("--post-cluster")

    result = await utils.run_shell_command(command)

    if not ok(result):
        return result  # pyright: ignore

    path = Path(output_folder, "clustering", "fastq_files")
    if not path.exists:
        return Err(RuntimeError(f"Expected the path `{path}` to exist as the command doesn't seem to have failed."))

    filepaths = []
    for root, _, files in path.walk():
        for file in files:
            filepath = Path(root, file)
            if filepath.suffix == ".fastq":
                filepaths.append(filepath)

    return Ok(filepaths)


async def main():
    species = "Allium_Ursinum"
    marker = utils.Markers.ITS

    output_base = Path(f"output/{species}/")
    output_nanoplot = Path(output_base, "nanoplot/")
    os.makedirs(output_nanoplot, exist_ok=True)
    output_filtered_reads = Path(output_base, "filtered_reads.fastq")
    output_cluster = output_base  # isONclust3 creates `cluster` path on its own

    # Run isONclust3 clustering
    cluster_filepaths = (await run_isONclust3(output_filtered_reads, output_cluster)).unwrap()
    print(cluster_filepaths)

    """
    # Decontamination (Cleaning for contaminations (selecting only clusters corresponding to angiosperms)

    # Setup paths
    folder = Path("cluster_output/seperated_clusters")  # fetching the clusters
    output_dir = Path("cluster_output/BLAST")  # okutput directory for BLAST results
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all relevant files
    fasta_files = (
        list(folder.glob("*.fasta"))
        + list(folder.glob("*.fa"))
        + list(folder.glob("*.fastaq"))
        + list(folder.glob("*.fastq"))
    )

    for fasta_file in fasta_files:
        # Convert .fastaq or .fastq to .fasta
        if fasta_file.suffix == ".fastq":
            fasta_converted = fasta_file.with_suffix(".fasta")
            fasta_file = utils.convert_fastq_to_fasta(fasta_file, fasta_converted)

        # Define output file path
        output_file = output_dir / f"{fasta_file.stem}_blast.out"

        # Run BLASTN
        run_blastn(fasta_file, "Database/Magnoliopsida_raxtax_db", output_file)

    # deleting all non plant clusters (empty files)
    # delete_empty_files("cluster_output/BLAST", recursive=True)
    """
