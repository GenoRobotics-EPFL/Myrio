import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import pathlib

    import polars as pl

    return pathlib, pl


@app.cell
def _(pathlib):
    filepath: pathlib.Path = pathlib.Path("_GenoRobotics/Myrio/ignore/bold_data_utf8.tsv")
    return (filepath,)


@app.cell
def _(filepath, pl):
    def _():
        pre_df = pl.read_csv(
            filepath,
            n_rows=0,
            quote_char=None,
            separator="\t",
            schema_overrides={"elev": pl.Float64},
        )
        return pre_df.columns

    columns = _()
    columns.remove("collection_note")
    columns.remove("lat")
    columns.remove("elev")
    columns.remove("coord_accuracy")
    columns
    return (columns,)


@app.cell
def _(columns, filepath, pl):
    df = pl.read_csv(filepath, separator="\t", columns=columns, quote_char=None, infer_schema=False)
    df = df.select(
        [
            "processid",
            "phylum_name",
            "class_name",
            "order_name",
            "family_name",
            "subfamily_name",
            "genus_name",
            "species_name",
            "subspecies_name",
            "markercode",
            "nucleotides",
        ]
    )

    df = df.filter(
        pl.col("markercode").is_in(["rbcL", "matK", "trnH-psbA", "ITS", "ITS2", "ITS1", "rbcL-like", "matK-like"])
    )

    df = df.filter(pl.col("nucleotides").is_not_null())
    df
    return (df,)


@app.cell
def _(phyllum, pl):
    def gen_fasta(filename: str, df: pl.DataFrame):
        # ('CAATB165-11', 'Tracheophyta', 'Magnoliopsida', 'Gentianales', 'Apocynaceae', None, 'Matelea', 'Matelea nigra', None, 'rbcL', '--------CC')
        def phylum(st):
            return f"phylum:{st.replace(' ', '_')}" if st is not None else ""
        def clas(st):
            return f"class:{st.replace(' ', '_')}" if st is not None else ""
        def order(st):
            return f"order:{st.replace(' ', '_')}" if st is not None else ""
        def family(st):
            return f"family:{st.replace(' ', '_')}" if st is not None else ""
        def genus(st):
            return f"genus:{st.replace(' ', '_')}" if st is not None else ""
        def species(st):
            return f"species:{st.replace(' ', '_')}" if st is not None else ""

        fasta_string = ""
        for row in df.rows():
            fasta_string += f">BOLD_PID={row[0]}|MARKER_CODE={row[9]};tax={phyllum(row[1])},{clas(row[2])},{order(row[3])},{family(row[4])},{genus(row[6])},{species(row[7])};\n{row[-1].strip().replace('-', 'N').replace('I', 'N')}\n"

        with open(f"_GenoRobotics/Myrio/ignore/{filename}.fasta", "w") as file:
            file.write(fasta_string)

    return (gen_fasta,)


@app.cell
def _(df, gen_fasta, pl):
    gen_fasta("Magnoliopsida_rbcL_raxdb", df.filter(pl.col("markercode").is_in(["rbcL", "rbcL-like"])))
    return


@app.cell
def _(df, gen_fasta, pl):
    gen_fasta("Magnoliopsida_matK_raxdb", df.filter(pl.col("markercode").is_in(["matK", "matK-like"])))
    return


@app.cell
def _(df, gen_fasta, pl):
    gen_fasta("Magnoliopsida_trnH-psbA_raxdb", df.filter(pl.col("markercode").is_in(["trnH-psbA"])))
    return


@app.cell
def _(df, gen_fasta, pl):
    gen_fasta("Magnoliopsida_ITS_raxdb", df.filter(pl.col("markercode").is_in(["ITS", "ITS1", "ITS2"])))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
