#! /bin/bash
# far from finished, do not use this yet
cargo install isonclust3
cargo install raxtax
uv sync
uv pip install
source .venv/bin/activate
uv pip install NanoPlot
