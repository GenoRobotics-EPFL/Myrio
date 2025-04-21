init:
    uv pip install -e .
    uv run lefthook install

# install the perca package
install:
    uv pip install -e .

alias build:=install

# run the perca cli with the provided arguments
run:
    @echo "Unavailable, run 'just install' then 'perca [ARGS]'"

# run all tests
test:
    uv run pytest -v

# run all benchmarks
bench:
    uv run pytest -v --benchmark-autosave --benchmark-warmup=on --benchmark-only

# run the ruff formatter
format:
    uv run ruff format

# run the ruff check
check:
    uv run ruff check --fix
