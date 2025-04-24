from Bio import SeqIO

fasta_file = "customtest/generated_dataset/sequence.fasta"
count = sum(1 for _ in SeqIO.parse(fasta_file, "fasta"))

print(f"📦 Total sequences in {fasta_file}: {count} (ITS)")

# Count frequency of each genus in the FASTA file

from Bio import SeqIO
from collections import Counter

def count_genus_frequencies(fasta_file):
    genus_counter = Counter()

    for record in SeqIO.parse(fasta_file, "fasta"):
        try:
            # Extract the genus from the header
            description = record.description
            species_part = description.split("|")[1]  # e.g. ">ID|Genus species|..."
            genus = species_part.strip().split()[0]
            genus_counter[genus] += 1
        except IndexError:
            continue  # skip malformed records

    return genus_counter

# === MAIN ===
if __name__ == "__main__":
    fasta_path = "customtest/Angiospermae_FASTA/matK_angiospermae_bold.fasta"
    genus_counts = count_genus_frequencies(fasta_path)

    # Convert to DataFrame for easier viewing/exporting
    import pandas as pd
    df_genus = pd.DataFrame(genus_counts.items(), columns=["Genus", "Count"])
    df_genus = df_genus.sort_values("Count", ascending=False).reset_index(drop=True)

    print(df_genus.head(20))  # show top 20 genera
    df_genus.to_csv("genus_frequency_table.csv", index=False)
    print("✅ Saved genus frequency table to: genus_frequency_table.csv")
