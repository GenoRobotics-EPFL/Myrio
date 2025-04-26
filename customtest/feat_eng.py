from Bio import SeqIO
from collections import defaultdict
import pandas as pd
import re
from tqdm import tqdm
import itertools

def clean_sequence(seq):
    return re.sub(r'[^ATCG]', '', seq.upper())

def count_kmers(seq, k):
    counts = defaultdict(int)
    for i in range(len(seq) - k + 1):
        kmer = seq[i:i+k]
        counts[kmer] += 1
    return counts

def normalize_counts(counts):
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()} if total > 0 else {}

def generate_all_kmers(k=5):
    bases = ["A", "C", "G", "T"]
    return ["".join(tup) for tup in itertools.product(bases, repeat=k)]

def build_kmer_dataset_fixed(fasta_file, k=5):
    fixed_kmers = generate_all_kmers(k)
    print(f"Using {len(fixed_kmers)} strand-specific k-mers (k={k})")

    data = []
    records = SeqIO.parse(fasta_file, "fasta")

    for record in tqdm(records):
        seq = clean_sequence(str(record.seq))
        label = record.description.split("|")[1].split()[0]  # Extract genus only
        kmer_counts = count_kmers(seq, k)
        norm_counts = normalize_counts(kmer_counts)

        row = {k: norm_counts.get(k, 0) for k in fixed_kmers}
        row["genus"] = label
        data.append(row)

    df = pd.DataFrame(data)
    return df

def save_as_parquet(df, output_path):
    df.to_parquet(output_path, index=False)
    print(f"✅ Saved cleaned k-mer dataset to: {output_path}")

# === MAIN ===
if __name__ == "__main__":
    fasta_path = "customtest/generated_dataset/generated.fasta"
    output_parquet = "customtest/generated_dataset/generated.parquet"
    k = 5

    df_kmers = build_kmer_dataset_fixed(fasta_path, k=k)
    save_as_parquet(df_kmers, output_parquet)
