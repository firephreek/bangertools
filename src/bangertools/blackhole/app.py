import numpy as np
import pynbody
import typer
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from bangertools import FilePath, PathList, OutputPath
from bangertools.blackhole.histogram import Histogram, StackedHistogram, BarHistogram
from bangertools.blackhole.reports import black_hole_log
from bangertools.blackhole.series import TimeSeries
from bangertools.common import util

bh_app = typer.Typer(help="Reports and data generation", pretty_exceptions_show_locals=True)


@bh_app.command(name="info")
def generate_blackholes_report(snapshot_path: FilePath):
    black_hole_log(snapshot_path or "./")


PROTON_MASS = 1.67 * 10 ** -27


@bh_app.command(name="rho")
def generate_blackhole_density_report(starlog_path: FilePath, output: OutputPath = None):
    starlog = pynbody.snapshot.tipsy.StarLog(starlog_path)
    starlog.physical_units()
    particles = starlog.stars[pynbody.filt.LowPass('tform', 0.0)]

    rhoform_ = particles["rhoform"].in_units("m_p cm^-3")  # * PROTON_MASS
    plt.hist(rhoform_, bins=10)
    plt.xlabel("rhoform")
    plt.ylabel("Number of particles")
    plt.title(f"[{starlog_path}]\nHistogram of rhoform for stars with tform < 0")
    plt.tight_layout()

    if not output:
        plt.show()
    else:
        plt.savefig(output)


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


@bh_app.command(name="tvd")
def generate_temperature_density_scatterplot(paths: PathList, output: OutputPath = None, fps=24):
    snapshot_paths = util.get_snapshots(paths)

    # Find global plot limits across all snapshots
    rho_min = np.inf
    rho_max = -np.inf
    temp_min = np.inf
    temp_max = -np.inf

    print("Calculating plot ranges...")

    for snapshot in snapshot_paths:
        sim = pynbody.load(snapshot)

        density = np.asarray(sim.g["rho"])
        temperature = np.asarray(sim.g["temp"])

        # Remove invalid values for log scaling
        valid = (
                np.isfinite(density) &
                np.isfinite(temperature) &
                (density > 0) &
                (temperature > 0)
        )

        density = density[valid]
        temperature = temperature[valid]

        rho_min = min(rho_min, density.min())
        rho_max = max(rho_max, density.max())

        temp_min = min(temp_min, temperature.min())
        temp_max = max(temp_max, temperature.max())

    print("Final ranges:")
    print("Density:", rho_min, rho_max)
    print("Temperature:", temp_min, temp_max)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    scatter = ax.scatter([], [], s=5, alpha=0.5)

    # Use log axes
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Add small margins around the data
    ax.set_xlim(rho_min * 0.8, rho_max * 1.2)
    ax.set_ylim(temp_min * 0.8, temp_max * 1.2)

    ax.set_xlabel(r'Density ($\rho$)')
    ax.set_ylabel(r'Temperature ($T$)')
    ax.set_title(f'Temperature vs Density - {paths[0].split("/")[0]}')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.minorticks_on()

    def update(snapshot):
        sim = pynbody.load(snapshot)

        density = np.asarray(sim.g["rho"])
        temperature = np.asarray(sim.g["temp"])

        valid = (
                np.isfinite(density) &
                np.isfinite(temperature) &
                (density > 0) &
                (temperature > 0)
        )

        points = np.column_stack((
            density[valid],
            temperature[valid]
        ))

        scatter.set_offsets(points)

        ax.set_title(snapshot)

        return scatter,

    ani = FuncAnimation(
        fig,
        update,
        frames=snapshot_paths,
        interval=50,
        blit=False
    )
    if output:
        ani.save(
            output,
            writer="ffmpeg",
            fps=fps,
            dpi=200
        )
    else:
        plt.show()
