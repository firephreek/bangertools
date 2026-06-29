import typer

from bangertools import FilePath
from .histogram import generate_hist
from .reports import black_hole_log
from ..common import util

bh_app = typer.Typer(help="Reports and data generation")


@bh_app.command(name="info")
def generate_blackholes_report(snapshot_path: FilePath = "./"):
    black_hole_log(snapshot_path)


@bh_app.command(name="hist")
def generate_histogram_report(snapshot_path: FilePath = "./"):
    snapshot_paths = util.get_snapshots(snapshot_path)
    generate_hist(snapshot_paths)
