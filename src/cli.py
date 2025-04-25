import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import aiofiles as aiof
from clypi import Command, Positional, Spinner, cprint
from clypi._components.spinners import _PerLineIO
from safe_result import Err, Ok, ok, safe_async
from typing_extensions import override

from consensus import spoa_consensus
from preprocessing import preprocessing
from raxtax import Raxtax
from selection import run_isONclust3
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

    @safe_async
    async def _run(self) -> None:
        async with Spinner("Checking filepath", capture=False) as spin:
            await asyncio.sleep(1.0)
            match check_filepath(self.filepath):
                case True:
                    await spin.done()
                case False:
                    await spin.fail()
                    raise RuntimeError("Filepath does not point to an existing file.")

        async with aiof.tempfile.TemporaryDirectory(prefix="myrio_") as tmp:
            tmp = Path(tmp)

            async with Spinner("Pre-processing reads", capture=False) as spin:
                input_fp = Path(self.filepath)
                filtered_reads_fp = Path(tmp, "reads.fastq")
                result = await preprocessing(input_fp, filtered_reads_fp)
                if not ok(result):
                    await spin.fail()
                    result.unwrap()
                await spin.done()

            cluster_fps: list[Path] = []
            async with Spinner("Selecting plant DNA", capture=False) as spin:
                input_fp = Path(tmp, "reads.fastq")
                result = await run_isONclust3(input_fp, tmp)
                match result:
                    case Ok(fps):
                        cluster_fps.extend(fps)
                        await spin.done(msg=f"Selecting plant DNA → # clusters = {len(fps)}")
                    case Err(error):
                        await spin.fail()
                        raise error

            async with Spinner("Generating a consensus sequence", capture=False) as spin:
                output_fp = Path(tmp, "consensus.fasta")
                executor = ProcessPoolExecutor(
                    max_workers=1
                )  # This allows us to run spoa_consensus fully outside the main Python process, so our spinner doesn't freeze.
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(executor, spoa_consensus, cluster_fps)
                match result:
                    case Ok(sequences):
                        string = "\n".join([f">consensus_sequence_from_cluster_{id}\n{seq}" for (id, seq) in sequences])
                        async with aiof.open(output_fp, "w") as file:
                            _ = await file.write(string)
                        async with aiof.open("consensus.fasta", "w") as file:
                            _ = await file.write(string)
                        await spin.done()
                    case Err(error):
                        await spin.fail()
                        raise error

            """ TODO
            async with Spinner("Assessing quality", capture=False) as spin:
                await asyncio.sleep(1.0)
                await spin.done()
            """

            async with Spinner("Indentifying the species", capture=False) as spin:
                input_fp = Path(tmp, "consensus.fasta")
                raxtax = (await Raxtax.build(input_fp, Path("./database/Magnoliopsida_raxdb.fasta"), tmp)).unwrap()
                await spin.done()

            raxtax.prettify_names()
            print(raxtax.df)  # .select(raxtax.df.columns[-8:]))


def main():
    cmd = Cli.parse()
    cmd.start()


if __name__ == "__main__":
    main()
