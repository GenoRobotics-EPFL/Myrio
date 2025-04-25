
def blastn_prediction(input_fp, tmp):

    number_of_consensus = 0
    with open(input_fp, 'r') as infile:
            while True:
                header = infile.readline()
                if not header:
                    break  # End of file
                sequence = infile.readline()
                plus_line = infile.readline()
                quality = infile.readline()
                
                with open(Path(tmp,f"consensus_fasta/{counter}.fasta"), 'w') as outfile:
                    outfile.write(header)
                    outfile.write(sequence)
                    outfile.write(plus_line)
                    outfile.write(quality)
                counter += 1

    result = []
    for i in range(number_of_consensus):
        
        for gene_name in gene_names:
            if not os.path.exists(Path(tmp, f"blast/{i}/{gene_name}")):
                os.makedirs(Path(tmp, f"blast/{i}/{gene_name}"))

            blastn_command = f"blastn -query  {str(Path(tmp,f"consensus_fasta/{counter}.fasta"))} -db ./database/blast_db/{gene_name} -out {str(Path(tmp, f"blast/{counter}/{gene_name}/id_result.xml"))} -outfmt 5 -max_hsps 1"
            print(blastn_command)
            
            await utils.exec_command(blastn_command.split())

            blast_records = NCBIXML.parse(open(Path(tmp, f"blast/{counter}/{gene_name}/id_result.xml"), "r"))
            blast_record = next(blast_records)  # you only have one query

            
            if len(blast_record.alignments) == 0:
                # print("NO IDENTIFICATION")
                continue

            for alignment in blast_record.alignments[:5]: # TODO

                sumcoverage = 0
                sumidentity = 0
                sumAlignLenth = 0

                for hsp in alignment.hsps:
                    if hsp.expect < 0.01:
                        sumcoverage += (hsp.query_end - hsp.query_start + 1)

                        sumidentity += hsp.identities
                        sumAlignLenth += hsp.align_length

                coverage = (sumcoverage / blast_record.query_length) * 100
                identity = (sumidentity / sumAlignLenth) * 100
                
                hsp = alignment.hsps[0]
                # print("IDENTIFICATION", alignment.hit_def, hsp.score, hsp.bits, coverage, identity)

                result.append({"def" : alignment.hit_def, "score" : hsp.score, "score_bits" : hsp.bits, "coverage" : coverage, "identity" : identity, "gene_name" : gene_name})

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

    ######## aggregate query results ############

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

    result_df = pl.DataFrame(parsed_raxtax_output, orient="row")
    .with_columns(
        pl.col("name").cast(pl.String),
        pl.col("occurences").cast(pl.Float64),
        pl.col("score").cast(pl.Float64),
        pl.col("bit_score").cast(pl.Float64),
        pl.col("identity").cast(pl.Float64),
        pl.col("converage").cast(pl.Float64),
    )
    .sort(by="score", descending=True)

    # print("20 best predictions")
    # print("===================")
    # print("sorted on average hit score in DB where a match of the species occurs (max 4 occurences, one for each gene)")
    # print("genus species (#occurences, (avg. score, avg. score bits, avg. identity, avg. coverage))")
    # print("===================")
    for i, (name, score_tuple) in enumerate(final_score_dict.items()):
        if i == 20:
            break
        result_df.insert(
                name, 
                score_tuple[0],
                score_tuple[0][0],
                score_tuple[0][1],
                score_tuple[0][2],
                score_tuple[0][3],
        )
        # print(i+1, name, score_tuple)
    return result_df