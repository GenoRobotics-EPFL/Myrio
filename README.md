Myrio is a command-line application designed to identify the taxonomy of a plant from a sample.

The name Myrio is inspired by the scientific name Myriophyllum spicatum, commonly known as Eurasian watermilfoil, an aquatic plant frequently found in the Léman.

_If you are a contributor, please refer to [this document](/CONTRIBUTING.md)._

> [!WARNING]
> This project is still in early development. It lacks many of the features we intend to implement, and a fair amount of technical debt remains under the hood (especially with certain dependencies). We don’t currently recommend installing or using Myrio unless you're contributing or experimenting.
> That said, the preliminary results using our simplified pipeline have been encouraging, and development will likely continue under the GenoRobotics umbrella, stay tuned.

### Installation (stub, for Linux)

You'll need the following tools installed beforehand: [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation), [`rust toolchain`](https://rustup.rs/), [`seqkit`](https://bioinf.shenwei.me/seqkit/)

### References
* Wei Shen, Botond Sipos, and Liuyang Zhao. 2024. SeqKit2: A Swiss Army Knife for Sequence and Alignment Processing. iMeta e191. doi:10.1002/imt2.191.
* raxtax: A k-mer-based non-Bayesian Taxonomic Classifier; Noah A. Wahl, Georgios Koutsovoulos, Ben Bettisworth, Alexandros Stamatakis; bioRxiv 2025.03.11.642618; doi: https://doi.org/10.1101/2025.03.11.642618
* Alexander J. Petri, Kristoffer Sahlin. De novo clustering of extensive long-read transcriptome datasets with isONclust3. bioRxiv 2024.10.29.620862; doi: https://doi.org/10.1101/2024.10.29.620862
* Ratnasingham, Sujeevan, and Paul D N Hebert. “bold: The Barcode of Life Data System (http://www.barcodinglife.org).” Molecular ecology notes vol. 7,3 (2007): 355-364. doi:10.1111/j.1471-8286.2007.01678.x
