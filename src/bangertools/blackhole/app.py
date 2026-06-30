from typing import Annotated

import pynbody
import typer

from bangertools import FilePath
from .histogram import Histogram
from .reports import black_hole_log
from ..common import util

bh_app = typer.Typer(help="Reports and data generation")


@bh_app.command(name="info")
def generate_blackholes_report(snapshot_path: FilePath):
    black_hole_log(snapshot_path or "./")


@bh_app.command(name="hist")
def generate_histogram_report(paths: Annotated[list[str], typer.Argument()] = "./",
                              output_file: str = ""):
    snapshot_paths = util.get_snapshots(paths)
    histogram = Histogram(snapshot_paths, 'tform',
                          title="Histogram of Star Particles with tform < 1",
                          xlabel="tform",
                          ylabel="Number of Star Particles",
                          bins=20)

    histogram.add_filter(pynbody.filt.LowPass('tform', 0.0))
    histogram.generate(output_file)
