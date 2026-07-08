import re
from pathlib import Path

from rich import print

from bangertools import PathList
from bangertools.common.state import appstate


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


def find_files(directory, extension, sort=True):
    """
    Returns all the files in the given directory that have the provided extension.
    :return: A list with Path objects representing files with the given extension.
    """
    files = []

    directory = Path(directory)
    for file in directory.iterdir():
        if file.is_file() and file.suffix == extension:
            files.append(file)

    return sorted(files) if sort else files


def find_starlog_file(directory):
    """
    Return the path to the starlog file in the given directory.
    :return: The first starlog file or None if no file with a '.starlog' extension exists
    """
    files = find_files(directory, '.starlog')
    if files:
        return files[0]
    return None


def print_verbose(message):
    if appstate.verbose:
        print(message)


def print_error(message):
    print(f"[bold red]{message}[/bold red]")
