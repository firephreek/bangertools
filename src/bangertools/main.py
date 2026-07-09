from typing import Annotated

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pynbody
import typer
from typer import Typer, Option, Argument

from bangertools import PathList
from bangertools.ahf.app import ahf_app
from bangertools.blackhole.app import bh_app
from bangertools.common import util
from bangertools.common.state import appstate
from bangertools.viz.app import viz_app

app = Typer()
app.add_typer(viz_app, name="view")
app.add_typer(bh_app, name="bh")
app.add_typer(ahf_app, name="ahf")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v"), ):
    appstate.verbose = verbose


OutputFile = Annotated[str, typer.Argument(help="File name to save the extracted data to.")]


@app.command("parq")
def save_data_to_parq_file(file_paths: PathList,
                           out: str = Argument(help="File name to save the extracted data to."),
                           cols: str = Option(..., "--cols", "-c", help="columns to extract"),
                           ignore_missing_cols: bool = False):
    """
    Extract a set of columns from all snapshots found in the provided paths and write them
    to a Pandas-compatible Parquet file.
    """

    snapshot_paths = util.get_snapshots(file_paths)
    cols = cols.split(",")
    writer = None

    try:
        for path in snapshot_paths:
            util.verbose(f"Loading {path}")
            sim = pynbody.load(path)

            util.verbose(f"Checking for missing columns")
            missing = [c for c in cols if
                       c not in sim.loadable_keys() and c not in sim.keys()]  # TODO: is there a reason we're not using `all_keys()` here? --snc

            if missing:
                if not ignore_missing_cols:
                    raise KeyError(f"Snapshot is missing fields: {missing}")
                else:
                    util.warn(f"Ignoring missing cols '{cols}' in {path}'")

            table = pa.table({
                col: np.asarray(sim[col])
                for col in cols
            })

            table = table.append_column(
                "source",
                pa.array([path.name] * table.num_rows)
            )

            if writer is None:
                if appstate.verbose:
                    util.verbose(f"Initializing Writer to {out}")
                    util.panel(f"Schema:", table.schema.to_string())

                writer = pq.ParquetWriter(out, table.schema, compression="zstd")

            util.verbose(f"Writing data to {out}")
            writer.write_table(table)
        # Final stats message
        writer.close()
        pf = pq.ParquetFile(out)
        print(pf.metadata)
    except Exception as e:
        util.err(e)


if __name__ == '__main__':
    app()
