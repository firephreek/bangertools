import typer

from bangertools import FilePath
from .reports import black_hole_log

bh_app = typer.Typer(help="Reports and data generation")


@bh_app.command(name="info")
def generate_blackholes_report(snapshot_path: FilePath = "./"):
    black_hole_log(snapshot_path)


@bh_app.command(name="hist")
def generate_histogram_report(snapshot_path: FilePath = "./"):
    pass
