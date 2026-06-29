import typer

from bangertools import FilePath

app = typer.Typer(help="Reports and data generation")


@app.command(name="blackholes")
def generate_blackholes_report(snapshot_path: FilePath = "./"):
    from bangertools.reports import convert
    convert.bh_log(snapshot_path)
