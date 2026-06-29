import typer

from bangertools import FilePath
from .blackhole import black_hole_log

app = typer.Typer(help="Reports and data generation")


@app.command(name="blackholes")
def generate_blackholes_report(snapshot_path: FilePath = "./"):
    black_hole_log(snapshot_path)
