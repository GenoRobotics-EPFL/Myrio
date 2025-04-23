import asyncio

from clypi import Command, Positional, Spinner, cprint
from clypi._components.spinners import _PerLineIO
from safe_result import Err, Ok, Result
from typing_extensions import override

from utils import check_filepath


# Monkey-wrench a fix for clypi
def safe_flush(self):
    if self.buffer and self.buffer[0]:
        self._new_line_cb(self.buffer[0])
    self.buffer = []


_PerLineIO.flush = safe_flush


class Cli(Command):
    filepath: Positional[str]

    @override
    async def run(self):
        match await self._run():
            case Ok(value):
                pass
            case Err(value):
                cprint("Error", fg="red", bold=True, end=f": {value}\n")

    async def _run(self) -> Result[None, RuntimeError]:
        async with Spinner("Checking filepath", capture=False) as spin:
            await asyncio.sleep(1.0)
            match check_filepath(self.filepath):
                case True:
                    await spin.done()
                case False:
                    await spin.fail()
                    return Err(RuntimeError("Filepath does not point to an existing file."))

        data = None  # noqa: F841
        async with Spinner("Pre-processing reads", capture=False) as spin:
            await asyncio.sleep(1.0)
            await spin.done()

        async with Spinner("Selecting plant DNA", capture=False) as spin:
            await asyncio.sleep(1.0)
            await spin.done()

        async with Spinner("Generating a consensus sequence", capture=False) as spin:
            await asyncio.sleep(1.0)
            await spin.done()

        async with Spinner("Assessing quality", capture=False) as spin:
            await asyncio.sleep(1.0)
            await spin.done()

        async with Spinner("Indentifying the species", capture=False) as spin:
            await asyncio.sleep(1.0)
            await spin.done()

        return Ok(None)


def main():
    cmd = Cli.parse()
    cmd.start()


if __name__ == "__main__":
    main()
