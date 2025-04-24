import pandas as pd

df = pd.read_parquet("customtest/generated_dataset/generated.parquet")  # Load the dataset
print(df.head())          # Show first few rows
print(df.columns)         # List all k-mer features
print(df.shape)           # Rows x Columns
print(df["genus"].value_counts())  # Check label distribution
print(df["genus"].nunique())  # Number of unique species
vc = df["genus"].value_counts()
valid_species = vc[vc >= 0]

vc.to_csv("genus_counts.csv")  # Save species counts to CSV
valid_species.to_csv("valid_genus_counts.csv")  # Save valid species counts to CSV