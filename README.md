## Myrio

Myrio, is a CLI-application to identify the taxonomy of a plant from a sample.

The name Myrio refers to the scientific name Myriophyllum spicatum, commonly known as the Eurasian watermilfoil,
an underwater plant commonly found in the Léman.

_If you are a contributor, please refer to [this document](/CONTRIBUTING.md)._

### Installation (on Linux)

> [!WARNING]
> Project not stabilized, and still missing many of the features we wanted to implement, we do not recommend attempting to install it at this stage, there is still a lot of jank under the hood to make it work, but it does work.

You'll need the following tools installed beforehand: [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation), [`rust toolchain`](https://rustup.rs/), [`seqkit`](https://bioinf.shenwei.me/seqkit/)

### References
* Wei Shen, Botond Sipos, and Liuyang Zhao. 2024. SeqKit2: A Swiss Army Knife for Sequence and Alignment Processing. iMeta e191. doi:10.1002/imt2.191.
* raxtax: A k-mer-based non-Bayesian Taxonomic Classifier; Noah A. Wahl, Georgios Koutsovoulos, Ben Bettisworth, Alexandros Stamatakis; bioRxiv 2025.03.11.642618; doi: https://doi.org/10.1101/2025.03.11.642618
* Alexander J. Petri, Kristoffer Sahlin. De novo clustering of extensive long-read transcriptome datasets with isONclust3. bioRxiv 2024.10.29.620862; doi: https://doi.org/10.1101/2024.10.29.620862
