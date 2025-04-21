from clypi import Command, Positional
from typing_extensions import override

from utils import check_filepath


class Cli(Command):
    filepath: Positional[str]

    @override
    async def run(self):
        print(f"filepath = `{self.filepath}`")
        print(
            f"The specified filepath {'exists' if check_filepath(self.filepath) else 'does not exist'}"
        )


def main():
    cmd = Cli.parse()
    cmd.start()
