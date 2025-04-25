import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from time import time

import aiofiles as aiof
from clypi import Command, Positional, Spinner, boxed, cprint
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
        _start = time()
        async with Spinner("Initializing", capture=False) as spin:
            await asyncio.sleep(1.0)
            match check_filepath(self.filepath):
                case True:
                    _diff = time() - _start
                    await spin.done(f"Initializing → {_diff:.3f} s")
                case False:
                    await spin.fail()
                    raise RuntimeError("Filepath does not point to an existing file.")

        async with aiof.tempfile.TemporaryDirectory(prefix="myrio_") as tmp:
            tmp = Path(tmp)
            _start = time()
            async with Spinner("Pre-processing reads", capture=False) as spin:
                input_fp = Path(self.filepath)
                filtered_reads_fp = Path(tmp, "reads.fastq")
                result = await preprocessing(input_fp, filtered_reads_fp)
                if not ok(result):
                    await spin.fail()
                    result.unwrap()
                _diff = time() - _start
                await spin.done(f"Pre-processing reads → {_diff:.3f} s")

            _start = time()
            cluster_fps: list[Path] = []
            async with Spinner("Clustering reads", capture=False) as spin:
                input_fp = Path(tmp, "reads.fastq")
                result = await run_isONclust3(input_fp, tmp)
                match result:
                    case Ok(fps):
                        cluster_fps.extend(fps)
                        _diff = time() - _start
                        await spin.done(msg=f"Clustering reads → {_diff:.3f} s ; {len(fps)} clusters")
                    case Err(error):
                        await spin.fail()
                        raise error

            _start = time()
            async with Spinner("Generating consensus", capture=False) as spin:
                output_fp = Path(tmp, "consensus.fasta")
                executor = ProcessPoolExecutor(
                    max_workers=1
                )  # This allows us to run spoa_consensus fully outside the main Python process, so our spinner doesn't freeze.
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(executor, spoa_consensus, cluster_fps)
                match result:
                    case Ok(sequences):
                        string = "\n".join([f">{id}\n{seq}" for (id, seq) in sequences])
                        async with aiof.open(output_fp, "w") as file:
                            _ = await file.write(string)
                        await spin.done(f"Generating consensus → {_diff:.3f} s")
                    case Err(error):
                        await spin.fail()
                        raise error

            """ TODO
            async with Spinner("Assessing quality", capture=False) as spin:
                await asyncio.sleep(1.0)
                await spin.done()
            """

            _start = time()
            async with Spinner("Running raxtax", capture=False) as spin:
                input_fp = Path(tmp, "consensus.fasta")
                result = await Raxtax.build(input_fp, Path("./database/Magnoliopsida_raxdb.fasta"), tmp)
                match result:
                    case Ok(val):
                        raxtax = val
                        await spin.done(f"Running raxtax → {_diff:.3f} s")
                    case Err(error):
                        await spin.fail()
                        raise error

            cprint("\n\n------ Best Raxtax Result  ------\n", bold=True)

            raxtax.prettify()
            best_raxtax_match = raxtax.df.row(0)
            print(
                boxed(
                    f"{best_raxtax_match[1]}",
                    width=70,
                    align="center",
                    title=f"Phylum: {best_raxtax_match[2]}",
                    color="magenta",
                )
            )
            print(
                boxed(
                    f"{best_raxtax_match[3]}",
                    width=65,
                    align="center",
                    title=f"Class: {best_raxtax_match[4]}",
                    color="red",
                )
            )
            print(
                boxed(
                    f"{best_raxtax_match[5]}",
                    width=60,
                    align="center",
                    title=f"Order: {best_raxtax_match[6]}",
                    color="yellow",
                )
            )
            print(
                boxed(
                    f"{best_raxtax_match[7]}",
                    width=55,
                    align="center",
                    title=f"Family: {best_raxtax_match[8]}",
                    color="green",
                )
            )
            print(
                boxed(
                    f"{best_raxtax_match[9]}",
                    width=50,
                    align="center",
                    title=f"Genus: {best_raxtax_match[10]}",
                    color="bright_blue",
                )
            )
            print(
                boxed(
                    f"{best_raxtax_match[11]}",
                    width=45,
                    align="center",
                    title=f"Species: {best_raxtax_match[12]}",
                    color="bright_cyan",
                )
            )

            cprint("------ Raxtax Results → saved to output/results.csv  ------\n", bold=True)

            print(raxtax.df.select(raxtax.df.columns[-8:]))
            raxtax.df.write_csv("output/results.csv")


def main():
    cmd = Cli.parse()
    cmd.start()


if __name__ == "__main__":
    main()
