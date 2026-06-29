import os
import re
from pathlib import Path

from bangertools import FilePath


def load_snapshot(file_path: str, convert_units: bool = True):
    import pynbody as pn
    snapshot = pn.load(file_path)
    if convert_units:
        snapshot.physical_units()  # converting code units to physical units
    return snapshot


def get_snapshots(dir_path: FilePath):
    snapshot_paths = [
        os.path.join(dir_path, p.name) for p in Path(dir_path).glob(f"*")

        if re.fullmatch(r".*\.\d{6}", p.name)
    ]

    snapshot_paths.sort()

    return snapshot_paths
