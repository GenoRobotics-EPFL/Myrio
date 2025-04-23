### Installation

This project uses [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) as its dependency manager. You can find its documentation [here](https://docs.astral.sh/uv/).

We also highly recommend installing [`just`](https://github.com/casey/just#installation), a command runner that simplifies common workflows.

Once installed, set up the project by running:
``` bash
git clone https://github.com/GenoRobotics-EPFL/Myrio
cd Myrio
just init
```

The `just init` command does the following:
``` yaml
init:
    uv sync
    uv pip install -e .
    uv run lefthook install
```
* Installs the project in an editable mode
* Sets-up pre-commit hooks to enforce a consistent code style

> [!NOTE]
> We use a `src/` and `test/` layout. This requires installing the package to avoid import issues.
>
> Check-out the [justfile](/justfile) or run `just --list` to view all available commands.


### Usage
Myrio is a CLI application. To run it:
``` bash
# Assuming the virtual environment is activated
# if not, then run `source .venv/bin/activate`
myrio [ARGS]
```

Alternatively, you can run it directly using uv:
``` bash
uv run src/cli.py [ARGS]
```

### Code Style & Best Practices

* Docstrings should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

Here's a quick example
``` py
def check_filepath(
    filepath: str | PathLike, readable: bool = False, writeable: bool = False
) -> bool:
    """Checks if a file exists and more.

    Args:
        filepath (str | PathLike): The filepath to check.
        readable (bool, optional): Also checks that the file can be read. Defaults to False.
        writeable (bool, optional): Also checks that the file can be written to. Defaults to False.

    Returns:
        bool: The result represented by a boolean.
    """
    filepath = Path(filepath)
    read_check = access(filepath, R_OK) if readable else True
    write_check = access(filepath, W_OK) if readable else True

    return filepath.is_file() and read_check and write_check
```

* **Error Handling**: Avoid raising exceptions where possible. Use [safe-result](https://github.com/overflowy/safe-result) to return exceptions as values.

* **Try to avoid excessive temp files**: Many tools we use are CLI-based. Prefer integrating their logic into our codebase if possible rather than relying on temp files and costly IO.

Example using [isONclust](https://github.com/ksahlin/isONclust), which has a Python API:
``` py
import modules as isonclust  # Yes, the package is named `modules`

# Extract and adapt only the needed logic from isONclust's CLI or script
```

* If temp files are necessary, use [aiofiles](https://github.com/Tinche/aiofiles) for asynchronous file operations.

* For shell command integration, prefer using [asyncio.subprocess](https://docs.python.org/3/library/asyncio-subprocess.html).

## The datasets (from 2024)

The datasets used are the sequencing results of multiple Genorobotics expeditions, more information by the method of extraction for each expedition can be found in the associated `general_info.csv` file:
- *demultiplexed data*: Every sample contains reads from only one species and one gene. The only demultiplexed expedition is the one [to Lausanne's botanical garden](data/expedition_jardin_botanique/) consisting of 10 samples of 5 different species and the 4 barcoding genes.
- *multiplexed data*: Every sample contains reads from only one species but up to 4 different genes. All of the remaning expeditions are multiplexed (i.e the [summer expedition](data/summer_expedition/) consisting of 12 samples of 12 different plants)

### data organization
- Each sub-folder represents a sample and spells out the sample's species, genes sequenced and barcode used.
- Each subfolder contains a `fastq` file containing the raw reads and a `fasta` file containing the species reference sequences for the genes amplified from the GenBank database
- Three csv files `general_info.csv`, `primer_info.csv` and `sample_info.csv` contain information about the expedition, the primers used and the species/genes for each sample respectively.
- The `tomato` folder is the only one to not to follow this organization, it is simply a compilation of sequencings from commercial tomato samples.

## How to create the reference databases for species identification (from 2024)

### Manual Download

BLASTn is run locally as an alignment tool to find the best match for our sample sequence from a database of known genetic sequences. This database must be downloadd manually for the four genes of interest from [GenBank](https://www.ncbi.nlm.nih.gov/genbank/)

Follow these steps:
- Go on the website: https://www.ncbi.nlm.nih.gov/nuccore
- For each of the four genes: MatK, rbcL, psbA-trnH, Internal Transcribed Spacer
   - Click on the `Advanced` search option (under the search bar)
   Type the name of the gene in the search bar and click on `search`
   - In the first bar, Type the name of the gene. In the second bar, replace `All Fields` by `Sequence Length` and select the range of sequence lengths to download (ex: 750:1500). The ranges proposed here provide a good basis for species identification while keeping the database size bearable:
        - MatK : 750 to 1500 -> ~110k Sequence, ~90Mo
        - rbcL : 600 to 1000 -> ~90k Sequence, ~80Mo
        - psbA-trnH : 400 to 800 -> ~60k Sequence, ~40Mo
        - ITS: 1000 to 35000

<u>**Note**</u>: Be sure to search for "Internal Transcribed Spacer" instead of "ITS" to get results
- Press on Search then Send to (corner top right) > Complete Record > File > Format = Fasta > Create File

<img width = "660" src = images/ncbi1.png>
<img width = "250" src = images/ncbi2.png>

### Creating the BLASTn databases
- Move the downloaded fasta file to the /db folder of your BLASTn installation directory
- open a terminal and place yourself in that /db directory using cd commands
- Use the makeblastdb command-line tool included with BLAST, replacing db_name.fasta by the name of the fasta you downloaded and output_name by the name of the four genes (use exactly these spellings and capitalization: matK, rbcL, psbA-trnH, ITS)

```bash
makeblastdb -in <db_name.fasta> -dbtype nucl -parse_seqids -out <output_name>
```
You can check it was correctly installed by asking infos about the resulting db :
```bash
blastdbcmd -db <db_name> -info
```
