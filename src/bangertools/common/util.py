import re
from pathlib import Path

from bangertools import PathList


def load_snapshot(file_path: str, convert_units: bool = True):
    import pynbody as pn
    snapshot = pn.load(file_path)
    if convert_units:
        snapshot.physical_units()  # converting code units to physical units
    return snapshot


def get_snapshots(paths: PathList):
    """
    Returns a sorted and de-duplicated collection of snapshot files from the provided paths.
    :param paths: A list of directories of files.
    """
    snapshot_paths = set()

    # If just a single path was passed as a string, turn it into a list for the next bit of code
    if isinstance(paths, str):
        paths = [paths]

    for path in map(Path, paths):
        if path.is_file():
            snapshot_paths.add(path)
        elif path.is_dir():
            snapshot_paths.update(
                p for p in path.iterdir()
                if re.fullmatch(r".*\.\d{6}", p.name)
            )

    return sorted(snapshot_paths)
