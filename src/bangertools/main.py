from typing import Annotated

from typer import Argument, Typer

from bangertools import utilities, convert, FilePath, SnapshotPath
from bangertools.viz.app import app as viz_app

# setup typer. This gives us a nice cli framework to call commands with
app = Typer()
app.add_typer(viz_app, name="view")


# This is a decorator that turns the function into a cli command (https://typer.tiangolo.com/tutorial/commands/arguments/)
# The Annotation is a type hint that typer can use to automatically populate the help menu.
@app.command(name="keys")
def snap_keys(file_path: FilePath):
    """
    List all the keys in the AHF halo catalog or snapshot file
    """
    return utilities.snap_keys(file_path)


# The SnapshotPath here is an Annotated class, just the one we defined earlier.
@app.command(name="minmax")
def dm_minmax(snapshot_path: SnapshotPath):
    """
    Print min/max DM particle mass and their ratio
    """
    return utilities.dm_minmax(snapshot_path)


@app.command(name="info")
def AHF_halo_info(ahf_path: FilePath):
    """
    Print total number of halos in AHF
    """
    return utilities.AHF_halo_info(ahf_path)


@app.command(name="mass")
def AHF_halo_mass(ahf_path: FilePath):
    """
    Print halo masses and most/least massive halo
    """
    return utilities.AHF_halo_mass(ahf_path)


@app.command(name="count")
def BH_count(snapshot_path: SnapshotPath):
    """
    Counts BHs in the snapshot
    """
    return utilities.BH_count(snapshot_path)


@app.command(name="halos")
def BH_halos(snapshot_path: SnapshotPath, ahf_path: FilePath = None):
    """
    Print which halos contain BHs and their masses
    If the ahf_path is not provided, it will try to find one using a `snapshot_path.*.AHF_halos` glob pattern
    """
    return utilities.BH_halos(snapshot_path, ahf_path)


@app.command(name="halo-masses")
def mass_range(file_path="halo_masses.csv"):
    """
    Print min/max halo mass from the saved CSV
    """
    return utilities.mass_range(file_path)


@app.command(name="write-csv")
def write_csvs(snapshot_path: SnapshotPath, ahf_path: FilePath = None):
    """
    Write halo_masses.csv and BH_masses.csv to be used for the occupation fraction plot
    """
    return utilities.write_csvs(snapshot_path, ahf_path)


@app.command(name="plot")
def plot_of_pretty(n: Annotated[int, Argument(help="Seed value")]):
    """
    Plot with bin counts annotated and color coding
    """
    return utilities.plot_of_pretty(n)


@app.command(name="vkick")
def conv_vkick(value: Annotated[float, Argument(help="The floating point value of the kick")]):
    """
    Convert a kick velocity from code units to km/s
    """
    return utilities.conv_vkick(value)


@app.command(name="fMhires")
def check_fMhires(ahf_path: FilePath):
    """
    Prints fMhires values for the first few halos to verify their values
    """
    return utilities.check_fMhires(ahf_path)


@app.command(name="zeros")
def check_snapshot_zeros(snapshot_path: SnapshotPath):
    """
    Check for zero mass particles in the snapshot
    """
    return utilities.check_snapshot_zeros(snapshot_path)


@app.command(name="fix-zeros")
def fix_zeros(snapshot_path: SnapshotPath):
    """
    Create a clean snapshot without zero mass particles and update startruns.txt to use it
    """
    return utilities.fix_zeros(snapshot_path)


@app.command(name="convert")
def convert_snapshot(snapshot_path: SnapshotPath):
    convert.convert(snapshot_path)


@app.command(name="info")
def info_command(file_path: FilePath):
    import pynbody
    import time

    t0 = time.time()
    s = pynbody.load(file_path)

    print("Load time:", time.time() - t0)
    print("Particles:", len(s))


if __name__ == '__main__':
    app()
