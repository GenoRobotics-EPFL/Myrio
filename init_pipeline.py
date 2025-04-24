import prepro
import clustering
import os
from pathlib import Path
import useful


Expedition = "flongle_fulvia_expedition"
Sample_barcode = 10

fastq, input, output = prepro.load_data(Expedition, Sample_barcode)

# Main function to run the preprocessing pipeline
prepro.run_nanoplot(fastq, output_dir=output)
prepro.preprocessing(fastq, "filtered_reads.fastq")
preproutput = os.path.join("prepr_output")
prepro.run_nanoplot("filtered_reads.fastq", output_dir=preproutput)


# Run Isonclust clustering
clustoutput = os.path.join("cluster_output")
clustering.run_isONclust("filtered_reads.fastq", clustoutput)

separated_clusters = os.path.join("cluster_output/seperated_clusters") 
clustering.write_clustered_fastq("cluster_output/final_clusters.tsv", "filtered_reads.fastq", separated_clusters)

# Cleaning for contaminations (selecting only clusters corresponding to angiosperms)


# Setup paths
folder = Path("cluster_output/seperated_clusters") #fetching the clusters
output_dir = Path("cluster_output/BLAST") # okutput directory for BLAST results
output_dir.mkdir(parents=True, exist_ok=True)

# Find all relevant files
fasta_files = list(folder.glob("*.fasta")) + list(folder.glob("*.fa")) + list(folder.glob("*.fastaq")) + list(folder.glob("*.fastq"))

for fasta_file in fasta_files:
    # Convert .fastaq or .fastq to .fasta
    if fasta_file.suffix == ".fastq":
        fasta_converted = fasta_file.with_suffix(".fasta")
        fasta_file = useful.convert_fastq_to_fasta(fasta_file, fasta_converted)

    # Define output file path
    output_file = output_dir / f"{fasta_file.stem}_blast.out"

    # Run BLASTN
    clustering.run_blastn(fasta_file, "Database/Magnoliopsida_raxtax_db", output_file)


#deleting all non plant clusters (empty files)
useful.delete_empty_files("cluster_output/BLAST", recursive=True)
