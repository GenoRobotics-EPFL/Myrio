from Bio import SeqIO
import time
import pandas as pd
from tqdm import tqdm

# === Load query and database FASTA files ===
query_file = "query_sequences.fasta"
db_file = "database_sequences.fasta"

queries = list(SeqIO.parse(query_file, "fasta"))
db = list(SeqIO.parse(db_file, "fasta"))

print(f"🔍 Queries: {len(queries)} | 🧬 Database: {len(db)}")

results = []

for query in tqdm(queries, desc="Searching best match"):
    qseq = str(query.seq).upper().replace("-", "").replace("N", "")
    best_id = None
    best_score = -1
    best_match = None

    start = time.time()

    for ref in db:
        rseq = str(ref.seq).upper().replace("-", "").replace("N", "")
        # Calculate crude identity
        matches = sum(a == b for a, b in zip(qseq, rseq))
        identity = matches / min(len(qseq), len(rseq))
        
        if identity > best_score:
            best_score = identity
            best_match = ref.id

    elapsed = time.time() - start

    results.append({
        "Query ID": query.id,
        "Best Match ID": best_match,
        "Best Identity": round(best_score, 4),
        "Time (s)": round(elapsed, 4)
    })

# === Save results ===
df = pd.DataFrame(results)
df.to_csv("best_matches_with_timings.csv", index=False)
print("✅ Saved to best_matches_with_timings.csv")
