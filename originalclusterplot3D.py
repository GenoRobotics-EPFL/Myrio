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
# Use t-SNE with 3 components instead of 2
tsne = TSNE(n_components=3, random_state=42)
X_3d = tsne.fit_transform(X.toarray())

df["x"] = X_3d[:, 0]
df["y"] = X_3d[:, 1]
df["z"] = X_3d[:, 2]

# Create 3D scatter plot
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

# Use Seaborn color palette
unique_clusters = df['cluster_id'].unique()
palette = sns.color_palette("tab10", n_colors=len(unique_clusters))
color_map = dict(zip(unique_clusters, palette))
colors = df['cluster_id'].map(color_map)

sc = ax.scatter(df["x"], df["y"], df["z"], c=colors, s=30)

# Add a basic legend
handles = [plt.Line2D([0], [0], marker='o', color='w',
                      label=cid, markersize=6, markerfacecolor=color_map[cid])
           for cid in unique_clusters]
ax.legend(handles=handles, title="Cluster", loc="upper left", bbox_to_anchor=(1.05, 1))

ax.set_title("3D t-SNE of DNA Clusters")
ax.set_xlabel("t-SNE 1")
ax.set_ylabel("t-SNE 2")
ax.set_zlabel("t-SNE 3")

plt.tight_layout()
plt.show()
