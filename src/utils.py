from os import R_OK, W_OK, PathLike, access
from pathlib import Path


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
