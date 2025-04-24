from Bio import SeqIO
import os

def convert_fastq_to_fasta(input_file, output_file):
    """
    Converts a FASTQ file to FASTA format using Biopython.
    """
    count = SeqIO.convert(input_file, "fastq", output_file, "fasta")
    print(f"Converted {count} records from {input_file.name} to {output_file.name}")
    return output_file


def delete_empty_files(folder_path, recursive=True):
    """
    Deletes all empty files in the given folder.
    
    Parameters:
    - folder_path (str): The path to the directory to scan.
    - recursive (bool): Whether to search subdirectories (default is True).
    """
    deleted_files = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            if os.path.getsize(filepath) == 0:
                os.remove(filepath)
                deleted_files.append(filepath)
        
        if not recursive:
            break  # Stop after the first directory if not recursive

    print(f"Deleted {len(deleted_files)} empty file(s).")
    return deleted_files
