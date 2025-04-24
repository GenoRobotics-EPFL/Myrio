import os
from Bio import SeqIO
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Read all FASTA files
def load_sequences_from_clusters(fasta_dir):
    data = []
    for filename in os.listdir(fasta_dir):
        if filename.endswith(".fasta") or filename.endswith(".fa"):
            cluster_id = os.path.splitext(filename)[0]
            for record in SeqIO.parse(os.path.join(fasta_dir, filename), "fasta"):
                data.append({
                    "read_id": record.id,
                    "sequence": str(record.seq),
                    "cluster_id": cluster_id
                })
    return pd.DataFrame(data)


df = load_sequences_from_clusters("cluster_output/seperated_clusters")

# Step 2: Convert to k-mers
def get_kmers(seq, k=6):
    return ' '.join([seq[i:i+k] for i in range(len(seq)-k+1)])

df["kmers"] = df["sequence"].apply(get_kmers)

# Step 3: Vectorize sequences
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df["kmers"])

# Step 4: Dimensionality reduction
tsne = TSNE(n_components=2, random_state=42)
X_2d = tsne.fit_transform(X.toarray())

df["x"] = X_2d[:, 0]
df["y"] = X_2d[:, 1]

# Step 5: Plot
plt.figure(figsize=(12, 9))
sns.scatterplot(data=df, x="x", y="y", hue="cluster_id", palette="tab10", s=30)
plt.title("2D Plot of DNA Clusters from IsONclust FASTAs")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
