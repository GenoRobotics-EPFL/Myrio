### Installation

This project uses [`uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) as its dependency manager. You can find its documentation [here](https://docs.astral.sh/uv/).

We also highly recommend installing [`just`](https://github.com/casey/just#installation), a command runner that simplifies common workflows.

Once installed, set up the project by running:
``` bash
git clone https://github.com/GenoRobotics-EPFL/Perca
cd Perca
just init
```

The `just init` command does the following:
``` yaml
init:
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
Perca is a CLI application. To run it:
``` bash
# Assuming the virtual environment is activated
# if not, then run `source .venv/bin/activate`
perca [ARGS]
```

Alternatively, you can run it directly using uv:
``` bash
uv run src/cli.py [ARGS]
```

### Code Style & Best Practices

* Docstrings should follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

Here's a quick exampl
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
