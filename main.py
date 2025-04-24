from src.manage_pipeline import run_pipeline
import time

base_input_path = "./data/expedition_data/flongle_fulvia_expedition/"
inputs_path = [
    ("Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6/Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6.fastq", ["MatK", "rbcL", "psbA-trnH", "ITS"]),
]


start = time.time()

results = []
for (path, gene_names) in inputs_path:
   results.append(run_pipeline(base_input_path+path, pipeline_name="default", gene_names=gene_names))
end = time.time()
print("TIME EXECUTION", int(end - start), "s")

print(results)

for result in results:
    for i, r in enumerate(result):
        print(i, r)