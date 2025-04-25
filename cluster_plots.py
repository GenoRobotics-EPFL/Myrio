import os
from Bio import SeqIO
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import re


def extract_number(filename) :
    """
    Extracts the first number from a filename.
    """
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else None

def load_sequences_from_clusters(fasta_dir, num_clusters=None):
    data = []
    fasta_files = [f for f in os.listdir(fasta_dir) if f.endswith(".fasta") or f.endswith(".fa")]
    fasta_files.sort(key=extract_number)  # Sort files to ensure consistent order
    if num_clusters is not None:
        fasta_files = fasta_files[:num_clusters]
    
    for filename in fasta_files:
        cluster_id = os.path.splitext(filename)[0]
        for record in SeqIO.parse(os.path.join(fasta_dir, filename), "fasta"):
            data.append({
                "read_id": record.id,
                "sequence": str(record.seq),
                "cluster_id": cluster_id
            })
    return pd.DataFrame(data)



df = load_sequences_from_clusters("cluster_output/seperated_clusters", 10)


def get_kmers(seq, k=6):
    return ' '.join([seq[i:i+k] for i in range(len(seq)-k+1)])

df["kmers"] = df["sequence"].apply(get_kmers)

# Vectorize sequences
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df["kmers"])

# Dimensionality reduction
tsne = TSNE(n_components=2, random_state=42)
X_2d = tsne.fit_transform(X.toarray())

df["x"] = X_2d[:, 0]
df["y"] = X_2d[:, 1]

'''
# Plot with unlabed clusters
# Plot
plt.figure(figsize=(12, 9))
sns.scatterplot(data=df, x="x", y="y", hue="cluster_id", palette="tab10", s=30)

# Add labels at the mean coordinates of each cluster
for cluster_id, group in df.groupby("cluster_id"):
    mean_x = group["x"].mean()
    mean_y = group["y"].mean()
    plt.text(mean_x, mean_y, str(cluster_id), fontsize=12, weight='bold',
             horizontalalignment='center', verticalalignment='center',
             bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

plt.title("2D t-SNE of DNA Clusters")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Cluster ID')
plt.xlabel("t-SNE 1")
plt.ylabel("t-SNE 2")
plt.tight_layout()
plt.show()
'''

# Plot with labeled clusters
# Use t-SNE with 3 components instead of 2
tsne = TSNE(n_components=3, random_state=42)
X_3d = tsne.fit_transform(X.toarray())

df["x"] = X_3d[:, 0]
df["y"] = X_3d[:, 1]
df["z"] = X_3d[:, 2]


# Ensure cluster_id is an integer
df['cluster_id'] = df['cluster_id'].astype(int)

# Define new labels and base colors
cluster_label_map = {
    0: '0-trnH',
    1: '1-trnH',
    2: '2-rbcl',
    3: '3-rbcl',
    4: '4-ITS',
    5: '5-ITS',
    6: '6-ITS',
}

group_colors = {
    'trnh': ['#a6cee3', '#1f78b4'],  # light blue, dark blue
    'rbcl': ['#b2df8a', '#33a02c'],  # light green, dark green
    'ITS':  ['#fdbf6f', '#ff7f00', '#ffa64c'],  # light to dark orange
    'others': sns.color_palette("tab10", 10)[6:]  # fallback for others
}

def get_label(cid):
    return cluster_label_map.get(cid, f'{cid}')

def get_color(cid):
    if cid in [0, 1]:
        return group_colors['trnh'][cid % 2]
    elif cid in [2, 3]:
        return group_colors['rbcl'][cid % 2]
    elif cid in [4, 5, 6]:
        return group_colors['ITS'][cid - 4]
    else:
        return group_colors['others'][(cid - 7) % len(group_colors['others'])]

# Map labels and colors
df['cluster_label'] = df['cluster_id'].apply(get_label)
df['color'] = df['cluster_id'].apply(get_color)

# 3D plot
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(df["x"], df["y"], df["z"], c=df["color"], s=30)

# Add cluster labels at the mean position of each cluster
for cluster_id, group in df.groupby("cluster_id"):
    mean_x = group["x"].mean()
    mean_y = group["y"].mean()
    mean_z = group["z"].mean()
    label = get_label(cluster_id)
    ax.text(mean_x, mean_y, mean_z, label,
            fontsize=10, weight='bold', color='black',
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

# Custom legend
unique_labels = df['cluster_label'].unique()
label_color_map = {label: df[df['cluster_label'] == label]['color'].iloc[0] for label in unique_labels}
handles = [plt.Line2D([0], [0], marker='o', color='w',
                      label=label, markersize=6, markerfacecolor=color)
           for label, color in label_color_map.items()]
ax.legend(handles=handles, title="Cluster", loc="upper left", bbox_to_anchor=(1.05, 1))

ax.set_title("3D t-SNE of DNA Clusters")
ax.set_xlabel("t-SNE 1")
ax.set_ylabel("t-SNE 2")
ax.set_zlabel("t-SNE 3")

fig.text(0.5, 0.01, "Clusters 7, 8 & 9 are unassigned", ha="center", fontsize=10, color='gray')

plt.tight_layout(rect=[0, 0.03, 1, 1])  
plt.show()




