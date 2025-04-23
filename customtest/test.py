import pandas as pd

df = pd.read_parquet("matK_kmer_cleaned.parquet")
print(df.head())          # Show first few rows
print(df.columns)         # List all k-mer features
print(df.shape)           # Rows x Columns
print(df["species"].value_counts())  # Check label distribution
print(df["species"].nunique())  # Number of unique species
vc = df["species"].value_counts()
valid_species = vc[vc >= 100].index
print(valid_species.shape)