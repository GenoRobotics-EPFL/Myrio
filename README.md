## Myrio

_If you are a contributor, please refer to [this document](/CONTRIBUTING.md)._

### code files
`main.py`                             entry point
`src/manage_pipeline.py`              might be usefull if we have multiple pipelines but not for the moment
`src/pipelines/piepline_default.py`   the actual pipeline running the commands

### data/output files
seqkit produce `filtered_reads.fastq`
isONclust produce `clustering` folder then write the clusters in fasta files in `clustering_fasta_files`
spoa write the consensus seq in fasta files in `spos`
medaka refine the consensus and write the result in `medaka/<cluster_index>/`, there is a `.bam` and a `.fastq`
mosdepth write the consensus quality in `mosdepth/<cluster_index>`
blast query results are written in `blast/cluster_index>/<gene_name>` 