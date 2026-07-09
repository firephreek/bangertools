import collections
from typing import Annotated

import numpy as np
import pynbody
import typer
from typer import Typer, Option

from bangertools import OutputPath, PathList
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


OutputFile = Annotated[str, Option(prompt_required=True, help="Optional file name to save the histogram to.")]


@app.command("cache")
def cache_snapshots(file_paths: PathList, out: OutputPath = "", cols: str = ""):
    # load the snapshot(s)
    snapshot_paths = util.get_snapshots(file_paths)

    cols = cols.split(",")
    data = collections.defaultdict(list)

    try:
        for path in snapshot_paths:
            util.print_verbose(f"Loading {path}")
            sim = pynbody.load(path)
            missing = [c for c in cols if
                       c not in sim.loadable_keys() and c not in sim.keys()]  # TODO: is there a reason we're not using `all_keys()` here? --snc

            if missing:
                raise KeyError(f"Snapshot is missing fields: {missing}")

            for col in cols:
                data[col].append(sim[col])  # don't use `extends` here...
            util.print_verbose(f"Columns extracted: {cols}")
    except Exception as e:
        util.print_error(e)

    data = {  # ...b/c concatenate is faster here since it uses C code under the hood
        key: np.concatenate(values)
        for key, values in
        data.items()
    }

    util.pv(f"Saving data to {out}")
    np.savez_compressed(out, **data)


if __name__ == '__main__':
    app()
