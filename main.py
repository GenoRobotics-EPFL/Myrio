from src.manage_pipeline import run_pipeline
import time

# base_input_path = "./data/expedition_data/flongle_fulvia_expedition/"
base_input_path = "./data/expedition_data/prunelle_without_purification_expedition/"
# inputs_path = [
#     ("Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6/Ficus_Benjamina_Qiagen_matk_rbcL_psbA-trnH_ITS_barcode6.fastq", ["MatK", "rbcL", "psbA-trnH", "ITS"]),
# ]

inputs_path = [
    ("Hederal_Helix_Fulvia_matk_rbcL_psbA-trnH_ITS_barcode3/Hederal_Helix_Fulvia_matk_rbcL_psbA-trnH_ITS_barcode3.fastq", ["MatK", "rbcL", "psbA-trnH", "ITS"]),
]


start = time.time()

results = []
for (path, gene_names) in inputs_path:
   results.append(run_pipeline(base_input_path+path, pipeline_name="default", gene_names=gene_names))
end = time.time()

# print(results)

for result in results:
    score_dict_per_gen = {"MatK" : {}, "rbcL" : {}, "psbA-trnH": {}, "ITS": {}}
    for i, r in enumerate(result):
        description = r["def"].split()
        genus = description[0]
        species = description[1]
        if "UNVERIFIED" in description[0]:
            genus = description[1]
            species = description[2]
        # print(genus, species)
        # print("score", r["score"])
        if f"{genus} {species}" not in score_dict_per_gen[r["gene_name"]]:
            score_dict_per_gen[r["gene_name"]][f"{genus} {species}"] = (r["score"], r["score_bits"], r["identity"], r["coverage"])
        else :
            if r["score"] > score_dict_per_gen[r["gene_name"]][f"{genus} {species}"][0]:
                score_dict_per_gen[r["gene_name"]][f"{genus} {species}"] = (r["score"], r["score_bits"], r["identity"], r["coverage"])

    # print(score_dict_per_gen)
    final_score_dict = {}
    for _, gene_score_dict in score_dict_per_gen.items():
        for name, score_tuple in gene_score_dict.items():
            if name not in final_score_dict:
                final_score_dict[name] = (1, score_tuple) # (number of occurence in gen dict, (score indicators))
            else:
                final_score_dict[name] = (final_score_dict[name][0]+1, 
                                            (   final_score_dict[name][1][0] + score_tuple[0], 
                                                final_score_dict[name][1][1] + score_tuple[1],
                                                final_score_dict[name][1][2] + score_tuple[2],
                                                final_score_dict[name][1][3] + score_tuple[3],
                                            )
                                         )

    # normalize score per occurence (do not penalize if 2 out of 4 occurence, or not ???)
    for name, occurence_score_tuple in final_score_dict.items():
        print(occurence_score_tuple)
        divider = occurence_score_tuple[0]
        # if divider < 2:
        #    divider = 1.5
        final_score_dict[name] = (occurence_score_tuple[0], 
                                            (   occurence_score_tuple[1][0]/divider, 
                                                occurence_score_tuple[1][1]/divider,
                                                occurence_score_tuple[1][2]/divider,
                                                occurence_score_tuple[1][3]/divider,
                                            )
                                         )

    final_score_dict = {k: v for k, v in sorted(final_score_dict.items(), key=lambda item: item[1][1][0], reverse=True)}

    print("20 best predictions")
    print("===================")
    print("sorted on average hit score in DB where a match of the species occurs (max 4 occurences, one for each gene)")
    print("genus species (#occurences, (avg. score, avg. score bits, avg. identity, avg. coverage))")
    print("===================")
    for i, (name, score_tuple) in enumerate(final_score_dict.items()):
        if i == 20:
            break
        print(i+1, name, score_tuple)
        

print("TIME EXECUTION", int(end - start), "s")
