import marimo

__generated_with = "0.23.9"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # OPC scenario explorer — BOSC roundabout cost estimates

        A reactive view of the six Tetra Tech *Opinion of Probable Project Cost*
        sub-estimates extracted from the PAAC PRR production (scanned exhibit
        pages 318-328). The data is the committed, reviewed artifact
        `data/extracted/aedg/roundabouts.summary.opc.yaml` — bundled read-only
        into this notebook's `public/` folder.

        > **Evidence note.** Dollar totals/subtotals are high-confidence;
        > quantities marked `~` in the source are approximate transcriptions.
        > This notebook **reads** the corpus and never writes to it.
        """
    )
    return


@app.cell
def _(mo):
    # mo.notebook_location() is the notebook dir (a Path) locally and the export
    # URL after WASM export. open() can't read a URL, so we go through urllib,
    # which Pyodide patches to use the browser fetch() — one code path for both.
    import urllib.request

    import yaml

    data_url = str(mo.notebook_location() / "public" / "roundabouts.summary.opc.yaml")
    with urllib.request.urlopen(data_url) as fh:  # trusted bundled asset, not user input
        doc = yaml.safe_load(fh.read())
    subs = doc["sub_estimates"]
    return doc, subs, yaml


@app.cell(hide_code=True)
def _(mo, subs):
    contingency = mo.ui.slider(
        start=0, stop=50, value=25, step=1, label="Contingency + inflation (%)"
    )
    selected = mo.ui.multiselect(
        options=[s["name"] for s in subs],
        value=[s["name"] for s in subs],
        label="Intersections",
    )
    mo.hstack([contingency, selected])
    return contingency, selected


@app.cell
def _(contingency, selected, subs):
    # Re-derive each total from the high-confidence construction subtotal under a
    # user-chosen contingency rate (the source convention is 25%).
    rate = 1 + contingency.value / 100
    rows = [
        {
            "name": s["name"],
            "construction_subtotal": s["construction_subtotal"],
            "modeled_total": round(s["construction_subtotal"] * rate),
            "source_total": s["total"],
        }
        for s in subs
        if s["name"] in set(selected.value)
    ]
    program_total = sum(r["modeled_total"] for r in rows)
    return program_total, rows


@app.cell(hide_code=True)
def _(mo, program_total, rows):
    mo.vstack(
        [
            mo.md(f"### Modeled program construction cost: **${program_total:,.0f}**"),
            mo.ui.table(rows, selection=None),
        ]
    )
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()
