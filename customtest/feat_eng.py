from Bio import SeqIO
from collections import defaultdict
import pandas as pd
import numpy as np
from tqdm import tqdm
import re

def reverse_complement(seq):
    complement = str.maketrans("ATCG", "TAGC")
    return seq.translate(complement)[::-1]

def canonical_kmer(kmer):
    rev_kmer = reverse_complement(kmer)
    return min(kmer, rev_kmer)

def count_kmers(seq, k):
    counts = defaultdict(int)
    for i in range(len(seq) - k + 1):
        kmer = canonical_kmer(seq[i:i+k])
        counts[kmer] += 1
    return counts

def normalize_counts(counts):
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total > 0 else {}

def clean_sequence(seq):
    # Keep only A, T, C, G (case-insensitive), remove everything else
    return re.sub(r'[^ATCG]', '', seq.upper())

def build_kmer_dataset_cleaned(fasta_file, k=5):
    records = SeqIO.parse(fasta_file, "fasta")
    all_kmers = set()
    data = []

    print("Indexing all unique k-mers...")
    for record in tqdm(records):
        seq = clean_sequence(str(record.seq))
        kmer_counts = count_kmers(seq, k)
        all_kmers.update(kmer_counts.keys())

    all_kmers = sorted(list(all_kmers))
    print(f"Total unique canonical k-mers (k={k}): {len(all_kmers)}")

    records = SeqIO.parse(fasta_file, "fasta")
    print("Building feature matrix...")

    for record in tqdm(records):
        seq = clean_sequence(str(record.seq))
        # label = record.description.split()[1]  # First word after accession
        label = record.description.split(" ")[1].split()[0]

        kmer_counts = count_kmers(seq, k)
        norm_counts = normalize_counts(kmer_counts)

        row = {k: norm_counts.get(k, 0) for k in all_kmers}
        row["species"] = label
        data.append(row)


    df = pd.DataFrame(data)
    return df

def save_as_parquet(df, output_path):
    df.to_parquet(output_path, index=False)
    print(f"✅ Saved cleaned k-mer dataset to: {output_path}")

# === MAIN ===
if __name__ == "__main__":
    fasta_path = "matK_angiospermae_bold.fasta"  # Adjust to your file path
    output_parquet = "matK_angiospermae_bold.parquet"
    k = 5

    df_kmers = build_kmer_dataset_cleaned(fasta_path, k=k)
    save_as_parquet(df_kmers, output_parquet)

