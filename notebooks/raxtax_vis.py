import marimo

__generated_with = "0.13.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import matplotlib.pyplot as plt
    import seaborn as sns
    from safe_result import Err, Ok

    import src.raxtax as rx

    sns.set_theme()
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 9
    plt.rcParams["ytick.labelsize"] = 9
    plt.rcParams["legend.fontsize"] = 9
    return Err, Ok, plt, rx


@app.cell
def _(Err, Ok, rx):
    async def get_df(input, db):
        match await rx.Raxtax.build(input=input, db=db):
            case Ok(rax):
                return rax.df
            case Err(err):
                print(err)

    return (get_df,)


@app.cell
async def _(get_df, plt):
    df1 = await get_df(
        input="./data/expedition_jardin_botanique/Ficus_religiosa_rbcL_barcode94/Ficus_religiosa_reference_seq.fasta",
        db="./database/Magnoliopsida_rbcL_raxdb.fasta",
    )

    def _():
        fig, ax1 = plt.subplots(1, 1, figsize=(6, 3))
        ax: plt.Axes = ax1

        ax.set_title("Ficus Religiosa Raxtax Results")
        ax.set_ylabel("score")
        for entry in df1.rows()[:-1]:
            plt.plot(
                [
                    "phylum",
                    "class",
                    "order",
                    "family",
                    "genus",
                    "species",
                ],
                [
                    entry[1],
                    entry[3],
                    entry[5],
                    entry[7],
                    entry[9],
                    entry[11],
                ],
                marker=".",
            )

        entry = df1.rows()[-1]
        plt.plot(
            [
                "phylum",
                "class",
                "order",
                "family",
                "genus",
                "species",
            ],
            [
                entry[1],
                entry[3],
                entry[5],
                entry[7],
                entry[9],
                entry[11],
            ],
            marker=".",
            label=entry[10].replace("_", " ").title(),
        )

        plt.legend()
        return fig

    _()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
