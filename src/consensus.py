import os
from pathlib import Path

import pysam
import spoa
from safe_result import safe


@safe
def spoa_consensus(cluster_fps: list[Path], second_pass: bool = False) -> list[dict[str, str]]:
    os.environ["OMP_NUM_THREADS"] = "1"
    consensus_sequences = []
    for cluster_fp in cluster_fps:  # TODO use threads to // and remove debug slicing
        with pysam.FastxFile(str(cluster_fp)) as f:
            sequences = [read.sequence for read in list(f)]

        min_cov = int(round(len(sequences) * 0.15))

        # run spoa will all sequence first
        cons, _ = spoa.poa(sequences, min_coverage=min_cov, genmsa=False)

        # second SPOA pass, using the previous result as first read
        if second_pass:
            cons, _ = spoa.poa([cons, *sequences], min_coverage=min_cov, genmsa=False)

        consensus_sequences.append({"cluster": cluster_fp.name, "sequence": cons})

    return consensus_sequences
