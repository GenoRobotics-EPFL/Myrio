### Installation

This project is managed using `uv`, information on how to install it can be found [here](https://github.com/astral-sh/uv?tab=readme-ov-file#installation), and its documentation [here](https://docs.astral.sh/uv/)

Furthermore it is also highly recommended to install `just`, for simplifying commands, information on how to install it can be found [here](https://github.com/casey/just#installation).

Assuming that is done, you should then run the following:
``` bash
git clone https://github.com/GenoRobotics-EPFL/Perca
cd Perca
just init
```

Taking a look at the project's [justfile](/justfile), shows what running `just init`does.
``` yaml
init:
    uv pip install -e .
    uv run lefthook install
```
It installs the package (+ as editable) and sets up the pre-commit hooks ensuring the style remains consistent.

Using a `src/` and `test/` directory would not be possible without using a build system and thus having to "install" our package.

### Usage

Perca is a cli application, if you wish to run the cli you can either run `just build` followed by `perca [ARGS]` or less succinctly `uv run src/cli.py -- [ARGS]`.

If you need to run a different python script file while testing something, run `uv run src/file.py`

### Style

For docstrings, you should adopt the [google style.](https://google.github.io/styleguide/pyguide.html)

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
