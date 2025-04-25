#! /bin/bash

cargo install isonclust3
cargo install raxtax
uv sync
uv pip install
source .venv/bin/activate
uv pip install NanoPlot
