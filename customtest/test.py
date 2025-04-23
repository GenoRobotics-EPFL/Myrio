import pandas as pd

df = pd.read_parquet("matK_angiospermae.parquet")
print(df.head())          # Show first few rows
print(df.columns)         # List all k-mer features
print(df.shape)           # Rows x Columns
print(df["species"].value_counts())  # Check label distribution
print(df["species"].nunique())  # Number of unique species
vc = df["species"].value_counts()
valid_species = vc[vc >= 0]

vc.to_csv("species_counts.csv")  # Save species counts to CSV
valid_species.to_csv("valid_species_counts.csv")  # Save valid species counts to CSV