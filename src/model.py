from pathlib import Path
from typing import Any
import xgboost as xgb
from collections import defaultdict
import re
from sklearn.decomposition import PCA
from Bio import SeqIO
import polars as pl

def use_model(model_path: Path, input_fasta_fp: Path):
    model = xgb.Booster()
    model.load_model(model_path)


def _fasta_to_parquet(input_fp: Path, output_dir: Path):
    output_fp = Path(output_dir, input_fp.stem + ".parquet")
    kmers_df = _build_kmer_dataset_cleaned(input_fp, format="fasta", k=5)
    kmers_df.write_parquet(output_fp)


def _build_kmer_dataset_cleaned(input_fp: Path, format: str = "fasta", k: int = 5) -> pl.DataFrame:

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


    records: Any = SeqIO.parse(input_fp, format)
    all_kmers = set()
    data = []

    # print("Indexing all unique k-mers...")
    for record in records:
        seq = clean_sequence(str(record.seq))
        kmer_counts = count_kmers(seq, k)
        all_kmers.update(kmer_counts.keys())

    all_kmers = sorted(list(all_kmers))

    # print(f"Total unique canonical k-mers (k={k}): {len(all_kmers)}")
    # print("Building feature matrix...")

    for record in records:
        seq = clean_sequence(str(record.seq))
        # label = record.description.split()[1]  # First word after accession
        label = record.description.split(" ")[1].split()[0]

        kmer_counts = count_kmers(seq, k)
        norm_counts = normalize_counts(kmer_counts)

        row = {k: norm_counts.get(k, 0) for k in all_kmers}
        row["species"] = label
        data.append(row)

    return pl.DataFrame(data)
