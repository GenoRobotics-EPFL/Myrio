# load fastq
# pass reads to pipeline to process
from src.pipelines import *

def run_pipeline(input_file_path, pipeline_name, gene_names):

    # load fastq ? (may pass directly files to tools)

    if pipeline_name == "default":
        return pipeline_default.run(input_file_path, gene_names)
    elif pipeline_name == "80_20":
        pass # TODO
    elif pipeline_name == "streaming":
        pass # TODO
    else:
        print("invalid pipeline name") # TODO print valid names