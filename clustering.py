import prepro
import subprocess
import os


def run_isONclust( fastq_file, output_folder):
    
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Construct the command
    command = [
        "isONclust",
        "--ont",
        "--fastq", fastq_file,
        "--outfolder", output_folder
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
        print("isONclust ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running isONclust: {e}")

def write_clustered_fastq(clusters_file, fastq_file, output_folder):
    """
    Runs isONclust write_fastq to separate reads into FASTQ files per cluster.

    Parameters:
        clusters_file (str): Path to the final_clusters.tsv file.
        fastq_file (str): Path to the original filtered FASTQ file.
        output_folder (str): Directory where the per-cluster FASTQ files will be written.
    """
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Construct the command
    command = [

        "isONclust", "write_fastq",
        "--clusters", clusters_file,
        "--fastq", fastq_file,
        "--outfolder", output_folder
    ]

    # Run the command
    try:
        subprocess.run(command, check=True)
        print("Clustered FASTQ files successfully written.")
    except subprocess.CalledProcessError as e:
        print(f"Error writing clustered FASTQ files: {e}")


# Cleaning for contaminations (selecting only clusters corresponding to angiosperms)

def run_blastn(query_file, db_path, output_file, evalue=1e-5, outfmt=6):
    """
    Runs BLASTN on a given query file against a specified database.

    Parameters:
    - query_file (str): Path to the FASTA file with the query sequence(s).
    - db_path (str): Path to the BLAST database (excluding file extensions).
    - output_file (str): Path to save the BLAST output.
    - evalue (float): E-value threshold for saving hits (default: 1e-5).
    - outfmt (int): BLAST output format (default: 6 = tabular).

    Returns:
    - None
    """
    blastn_cmd = [
        "blastn",
        "-query", query_file,
        "-db", db_path,
        "-out", output_file,
        "-evalue", str(evalue),
        "-outfmt", str(outfmt)
    ]

    try:
        subprocess.run(blastn_cmd, check=True)
        print(f"BLASTN completed. Results saved to '{output_file}'")
    except subprocess.CalledProcessError as e:
        print(f"BLASTN failed with error: {e}")
