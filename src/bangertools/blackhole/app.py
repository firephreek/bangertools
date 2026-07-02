import numpy as np
import pynbody
import typer

from bangertools import FilePath, PathList
from .histogram import Histogram, StackedHistogram, OutputPath, BarHistogram
from .reports import black_hole_log
from .series import TimeSeries
from ..common import util

bh_app = typer.Typer(help="Reports and data generation")


@bh_app.command(name="info")
def generate_blackholes_report(snapshot_path: FilePath):
    black_hole_log(snapshot_path or "./")


@bh_app.command(name="hist")
def generate_histogram_report(key: str, paths: PathList = "./", output: OutputPath = None):
    """
    Generates a histogram of blackholes found in the provided snapshots.
    :param paths: One more or paths with snapshot files or explicit snapshot files
    :param output: Optional. If provided, the plot will be saved to this file instead of being shown
    """
    snapshot_paths = util.get_snapshots(paths)
    histogram = Histogram(snapshot_paths, key,
                          title=f"Histogram of Star Particles with {key} < 1",
                          xlabel=key,
                          ylabel="Number of Star Particles",
                          bins=20)

    histogram.add_filter(pynbody.filt.LowPass('tform', 0.0))
    histogram.add_transform(lambda values: [k * -1 for k in values])
    histogram.generate(output)


@bh_app.command(name="stack_hist")
def generate_stacked_histogram(paths: PathList, output: OutputPath = None):
    stacked_histogram = StackedHistogram('tform',
                                         title="Histogram of Star Particles with tform < 1",
                                         xlabel="tform",
                                         ylabel="Number of Star Particles",
                                         legend=[],
                                         bins=20)

    filter = pynbody.filt.LowPass('tform', 0.0)
    transform = lambda values: [k * -1 for k in values]
    for i, path in enumerate(paths):  # TODO: Needs some good logging here
        stacked_histogram.add_snapshots(path, filter=filter, transform=transform)
    stacked_histogram.generate(output)


@bh_app.command(name="bar_hist")
def generate_stacked_histogram(paths: PathList, output: OutputPath = None):
    stacked_histogram = BarHistogram('rhoform',
                                     title="Histogram of Star Particles with tform < 1",
                                     xlabel="rhoform",
                                     ylabel="Number of Star Particles",
                                     legend=[],
                                     bins=20)

    filter = pynbody.filt.LowPass('tform', 0.0)
    transform = lambda values: [k * -1 for k in values]
    for i, path in enumerate(paths):  # TODO: Needs some good logging here
        stacked_histogram.add_snapshots(path, filter=filter, transform=transform)
    stacked_histogram.generate(output)


@bh_app.command(name="timeseries")
def generate_timeseries_plot(paths: PathList, output: OutputPath = None):
    snapshot_paths = util.get_snapshots(paths)

    timeseries = TimeSeries(snapshot_paths,
                            'tempEff',
                            title="Time vs Avg Temp",
                            ylabel="Temp"
                            )

    # timeseries.add_filter(pynbody.filt.LowPass('tform', 0.0))
    timeseries.add_transform(lambda values: np.average(values))
    timeseries.generate(output)
