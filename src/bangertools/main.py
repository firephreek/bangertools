import typer
from typer import Typer, Option

from bangertools import PathList
from bangertools.ahf.app import ahf_app
from bangertools.blackhole.app import bh_app
from bangertools.common.parq import save_data_to_parq_file
from bangertools.common.util import appstate
from bangertools.viz.app import viz_app

app = Typer()

app.add_typer(viz_app, name="view")
app.add_typer(bh_app, name="bh")
app.add_typer(ahf_app, name="ahf")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v"), ):
    appstate.verbose = verbose


@app.command("keys")
def get_keys(file_path: str):
    from bangertools import ahf
    ahf.app.snap_keys(file_path)


@app.command("parq")
def sve_data_to_parq_file(file_paths: PathList,
                          out: str = Option(..., "--out", "-o", help="File name to save the extracted data to"),
                          cols: str = Option(..., "--cols", "-c",
                                             help="The columns to be extracted into the new file"),
                          exclude_source: bool = Option(False, "--no-source",
                                                        help="If set, the source column will not be added to the export"),
                          ignore_missing_cols: bool = Option(False, "--ignore-missing-cols",
                                                             help="Snapshots that are missing columns will be skipped unless this is set.")):
    save_data_to_parq_file(file_paths, out, cols, exclude_source, ignore_missing_cols)


if __name__ == '__main__':
    app()
