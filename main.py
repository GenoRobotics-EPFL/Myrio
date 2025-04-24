from src.manage_pipeline import run_pipeline
import time

base_input_path = "./data/expedition_data/flongle_fulvia_expedition/"
# inputs_path = [
#     ("Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6/Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6.fastq", ["MatK", "rbcL", "psbA-trnH", "ITS"]),
# ]

inputs_path = [
    ("Cymbopogon_Citrus_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode10/Cymbopogon_Citrus_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode10.fastq", ["MatK", "rbcL", "psbA-trnH", "ITS"]),
]


start = time.time()

results = []
for (path, gene_names) in inputs_path:
   results.append(run_pipeline(base_input_path+path, pipeline_name="default", gene_names=gene_names))
end = time.time()

print(results)

for result in results:
    score_dict_per_gen = {"MatK" : {}, "rbcL" : {}, "psbA-trnH": {}, "ITS": {}}
    for i, r in enumerate(result):
        description = r["def"].split()
        genus = description[0]
        species = description[1]
        if "UNVERIFIED" in description[0]:
            genus = description[1]
            species = description[2]
        print(genus, species)
        print("score", r["score"])
        if f"{genus} {species}" not in score_dict_per_gen[r["gene_name"]]:
            score_dict_per_gen[r["gene_name"]][f"{genus} {species}"] = r["score"]
        else :
            if r["score"] > score_dict_per_gen[r["gene_name"]][f"{genus} {species}"]:
                score_dict_per_gen[r["gene_name"]][f"{genus} {species}"] = r["score"]

    print(score_dict_per_gen)
    final_score_dict = {}
    for _, gene_score_dict in score_dict_per_gen.items():
        for name, score in gene_score_dict.items():
            if name not in final_score_dict:
                final_score_dict[name] = score
            else:
                final_score_dict[name] += score
            
    final_score_dict = {k: v for k, v in sorted(final_score_dict.items(), key=lambda item: item[1], reverse=True)}

    print("10 best predictions")
    print("===================")
    for i, (name, score) in enumerate(final_score_dict.items()):
        print(name, score)
        if i == 10:
            break

print("TIME EXECUTION", int(end - start), "s")
