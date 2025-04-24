import sys
import os
import pysam
from Bio.Blast import NCBIXML

import spoa

def run(input_file_path, gene_names):

    print("starting pipeline default")

    # TODO uncomment commands later

    ENABLE_LONG_TIME_STUFF = True

    if ENABLE_LONG_TIME_STUFF:
        os.system("rm -rf ./data/output/*")

    ### seqkit filter
    print("====================== SEQKIT")
    filtered_read_file_name = "filtered_reads.fastq"
    seqkit_command = f"seqkit seq -Q 10 -m 300 {input_file_path} -o ./data/output/{filtered_read_file_name}"
    if ENABLE_LONG_TIME_STUFF:
        os.system(seqkit_command) # TODO

    ### (NanoPlot)

    ### isONclust clustering
    print("====================== isONclust")
    clustering_folder_name = "clustering"
    isONclust_command = f"isONclust --ont --fastq ./data/output/{filtered_read_file_name} --outfolder ./data/output/{clustering_folder_name}"
    if ENABLE_LONG_TIME_STUFF:
        os.system(isONclust_command) # TODO
    clustering_fasta_files_folder_name = "clustering_fasta_files"
    isONclust_command2 = f"isONclust write_fastq --clusters ./data/output/{clustering_folder_name}/final_clusters.tsv --fastq ./data/output/{filtered_read_file_name} --outfolder ./data/output/{clustering_fasta_files_folder_name} --N 10"
    if ENABLE_LONG_TIME_STUFF:
        os.system(isONclust_command2) # TODO


    ### spoa draft consensus

    print("====================== SPOA")
    clustering_fasta_files_folder_path = f"./data/output/{clustering_fasta_files_folder_name}"
    cluster_files = [ f for f in os.listdir(clustering_fasta_files_folder_path) if os.path.isfile(os.path.join(clustering_fasta_files_folder_path, f))]

    draft_cons_fasta_files_folder_name = "spoa"
    for cluster_file in cluster_files: # TODO use threads to // and remove debug slicing
        print("SPOA process ", cluster_file)
        with pysam.FastxFile(clustering_fasta_files_folder_path+"/"+cluster_file, "r") as f:    
            sequences = [read.sequence for read in list(f)]
        
        min_cov = int(round(len(sequences) * 0.15))

        # TODO
        if ENABLE_LONG_TIME_STUFF:
            # run spoa will all sequence first
            cons, _ = spoa.poa(sequences, min_coverage=min_cov, genmsa=False)

            print("SPOA second pass on ", cluster_file)
            # run spoa a second time with the previous result as first read
            cons, _ = spoa.poa([cons, *sequences], min_coverage=min_cov, genmsa=False)

            spoa_cons_file_path = f"./data/output/spoa/{cluster_file}"
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(spoa_cons_file_path), exist_ok=True)
            with open(spoa_cons_file_path, "w+") as f:
                f.write(">Consensus")
                f.write("\n")
                f.write(cons)
                f.write("\n")


    ### medaka refine consensus

    print("====================== shorten fasta cluster read header to work with samtools")
    for cluster_file in cluster_files:
        with open(clustering_fasta_files_folder_path+"/"+cluster_file, 'r') as infile, open(clustering_fasta_files_folder_path+"/short_header_"+cluster_file, 'w') as outfile:
            while True:
                header = infile.readline()
                if not header:
                    break  # End of file
                sequence = infile.readline()
                plus_line = infile.readline()
                quality = infile.readline()
                
                # Truncate header to first 50 characters (adjust as needed)
                truncated_header = header[:250].rstrip() + '\n'
                
                outfile.write(truncated_header)
                outfile.write(sequence)
                outfile.write(plus_line)
                outfile.write(quality)

    print("====================== MEDAKA")

    cons_fasta_files_folder_name = "medaka"

    draft_cons_fasta_files_folder_path = f"./data/output/{draft_cons_fasta_files_folder_name}"
    draft_cons_files = [ f for f in os.listdir(draft_cons_fasta_files_folder_path) if os.path.isfile(os.path.join(draft_cons_fasta_files_folder_path, f))]
    for i, (draft_cons_file, cluster_file) in enumerate(zip(draft_cons_files, cluster_files)): # TODO use threads to //
        print(draft_cons_file)
        medakaCommand = f"medaka_consensus -q -i {clustering_fasta_files_folder_path}/short_header_{cluster_file} -d {draft_cons_fasta_files_folder_path}/{draft_cons_file} -o ./data/output/{cons_fasta_files_folder_name}/{i} " # -m r941_min_high_g303
        if ENABLE_LONG_TIME_STUFF:
            os.system(medakaCommand) # TODO

    ### mosdepth evaluate consensus quality

    print("====================== MOSDEPTH")
    consensus_folder_and_bam_files = [ f+"/calls_to_draft.bam" for f in os.listdir(f"./data/output/{cons_fasta_files_folder_name}") if os.path.isdir(os.path.join(f"./data/output/{cons_fasta_files_folder_name}", f))]

    print("cons, files", consensus_folder_and_bam_files)

    mosdepth_folder_path = "./data/output/mosdepth"

    for i, cons_file in enumerate(consensus_folder_and_bam_files):

        mosdepth_current_cons_path = f"{mosdepth_folder_path}/{i}"
        if not os.path.exists(mosdepth_current_cons_path):
            os.makedirs(mosdepth_current_cons_path)

        # first run mosdepth
        mosdepth_command = f"mosdepth {mosdepth_current_cons_path}/ ./data/output/{cons_fasta_files_folder_name}/{cons_file}"
        print(mosdepth_command)
        os.system(mosdepth_command)

        # uncompress output data from mosdepth
        gzip_command = f"gzip -f -dk {mosdepth_current_cons_path}/.per-base.bed.gz"
        print(gzip_command)
        os.system(gzip_command)

    # TODO do smth with mosdepth result

    ### blastn / mmseq2 search DB

    print("====================== BLAST")

    consensus_folder_and_fastq_files = [ f+"/consensus.fastq" for f in os.listdir(f"./data/output/{cons_fasta_files_folder_name}") if os.path.isdir(os.path.join(f"./data/output/{cons_fasta_files_folder_name}", f))]

    result = []
    for i, cons_file in enumerate(consensus_folder_and_fastq_files):
        
        for gene_name in gene_names:
            if not os.path.exists(f"./data/output/blast/{i}/{gene_name}"):
                os.makedirs(f"./data/output/blast/{i}/{gene_name}")

            blastn_command = f"blastn -query  ./data/output/{cons_fasta_files_folder_name}/{cons_file} -db ./data/blast_db/{gene_name} -out ./data/output/blast/{i}/{gene_name}/id_result.xml -outfmt 5 -max_hsps 1"
            print(blastn_command)
            os.system(blastn_command)

            blast_records = NCBIXML.parse(open(f"./data/output/blast/{i}/{gene_name}/id_result.xml", "r"))
            blast_record = next(blast_records)  # you only have one query

            
            if len(blast_record.alignments) == 0:
                print("NO IDENTIFICATION")
                continue

            for alignment in blast_record.alignments[:5]: # TODO

                sumcoverage = 0
                sumidentity = 0
                sumAlignLenth = 0

                for hsp in alignment.hsps:
                    if hsp.expect < 0.01:
                        sumcoverage += (hsp.query_end - hsp.query_start + 1)

                        sumidentity += hsp.identities
                        sumAlignLenth += hsp.align_length

                coverage = (sumcoverage / blast_record.query_length) * 100
                identity = (sumidentity / sumAlignLenth) * 100
                
                print("IDENTIFICATION", alignment.hit_def, coverage, identity)

                result.append((alignment.hit_def, coverage, identity))

    return result
