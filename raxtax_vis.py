import marimo

__generated_with = "0.13.2"
app = marimo.App(width="full")


@app.cell
def _():
    import matplotlib.pyplot as plt
    import polars as pl
    import seaborn as sns
    from safe_result import Err, Ok

    import src.raxtax as rx

    sns.set_theme()
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams["legend.fontsize"] = 10
    return Err, Ok, pl, rx


@app.cell
async def _(Err, Ok, pl, rx):
    async def get_df(input, db):
        match await rx.Raxtax.build(input=input, db=db):
            case Ok(rax):
                return rax.df.sort(pl.col("species_score"), descending=True)
            case Err(err):
                print(err)

    df = await get_df(
        input="./data/expedition_jardin_botanique/Ficus_religiosa_rbcL_barcode94/Ficus_religiosa_reference_seq.fasta",
        db="./database/Magnoliopsida_rbcL_raxdb.fasta",
    )
    return


@app.cell
def _(pl):
    def plot(df: pl.DataFrame):
        pass

    return


if __name__ == "__main__":
    app.run()
