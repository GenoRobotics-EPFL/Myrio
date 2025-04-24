import os
import os.path as ospath
import subprocess
from Bio import SeqIO

#Loading the data

def load_data(input_expedition_folder, barcode_nb):
    """
    Load data paths for a given expedition and barcode.
    
    Parameters:
        input_expedition_folder (str): Folder name inside 'data/'.
        barcode_nb (int): Barcode number to search for.

    Returns:s
        input_fastq_path (str): Path to the .fastq file.
        input_ref_path (str): Path to the .fasta reference file.
        output_path (str): Path for the output directory.
    """
    input_expedition_path = ospath.join("data", input_expedition_folder)
    input_folder_path = None

    # Search for the correct barcode folder
    for root, dirs, files in os.walk(input_expedition_path):
        if root.endswith(f"barcode{barcode_nb}"):
            input_folder_path = root
            break

    if input_folder_path is None:
        raise ValueError(f"Could not find folder for barcode {barcode_nb}.")

    input_fastq_path = input_ref_path = input_fastq_filename = None

    # Search for FASTQ and FASTA files in the barcode folder
    for _, _, files in os.walk(input_folder_path):
        for file in files:
            if file.endswith(".fastq"):
                input_fastq_path = ospath.join(input_folder_path, file)
                input_fastq_filename = file
            elif file.endswith(".fasta"):
                input_ref_path = ospath.join(input_folder_path, file)

    if not input_fastq_path:
        raise ValueError("No .fastq file found in the directory.")

    print(f"Pipeline will run on file {input_fastq_path}")
    base_name = input_fastq_filename[:-6]
    output_path = ospath.join("output", base_name)
    print(f"Results can be found in {output_path}")

    return input_fastq_path, input_ref_path, output_path

def filter_fastq_with_seqkit(input_file, output_file, min_len=150, min_qual=10,max_qual=60):
    # Construct the SeqKit command
    command = [
        "seqkit", "seq",
        "-Q", str(min_qual),   # Minimum quality
        "-R", str(max_qual),   # Maximum quality
        "-m", str(min_len),    # Minimum sequence length
        input_file,
        "-o", output_file
    ]
 
    # Execute the command
    subprocess.run(command, check=True)
    print(f"Filtered reads written to {output_file}")

#Preprocessing function
def preprocessing(input_fastq, output_fastq):
    read_check(input_fastq)
    filter_fastq_with_seqkit(input_fastq, output_fastq)

#visualization 
def run_nanoplot(input_fastq, output_dir="nanoplot_results"):
    """
    Runs NanoPlot to generate quality and length distribution graphs from a FASTQ file.

    Parameters:
        input_fastq (str): Path to the FASTQ file.
        output_dir (str): Directory where NanoPlot outputs will be saved.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Build command
   
    cmd = [
    "NanoPlot",
    "--fastq", input_fastq,
    "--outdir", output_dir,
    "--verbose",
    "--N50",
    "--plots", "kde",  # or all
    "--loglength"
]

    print(f"Running NanoPlot:\n{' '.join(cmd)}")
    subprocess.run(cmd, check=True)





