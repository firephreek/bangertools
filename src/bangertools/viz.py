import re
from pathlib import Path

import typer

import bangertools.lib.viewer as viewer
from bangertools import FilePath

app = typer.Typer(help="Data visualization commands")


# @app.command(name="build_npz")
# def build_npz_command(
#         file_path: FilePath = "./core_trajectories.npz"):  # TODO: Make this a directory and a file and default to local and this name for either if they're not present.
#     viewer.build_core(file_path)

#
# @app.command(name="collapse")
# def view_npz_command(npz_path: FilePath = "./core_trajectories.npz"):
#     canvas = scene.SceneCanvas(
#         keys="interactive",
#         bgcolor="black",
#         size=(1800, 1000),
#         show=True,
#     )
#
#     return viewer.collapse_viewer(dir_path=npz_path, canvas=canvas)


@app.command(name="render")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    # Default to finding files that match our ChaNGa output

    snapshot_paths = [
        p.name for p in Path(dir_path).glob(f"*")
        if re.fullmatch(r".*\.\d{6}", p.name)
    ]

    player = viewer.Player(snapshot_paths)

    player.start()


if __name__ == "__main__":
    app()
