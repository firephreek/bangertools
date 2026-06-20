import typer

import bangertools.lib.viewer as viewer
from bangertools import FilePath

app = typer.Typer(help="Data visualization commands")


@app.command(name="build_npz")
def build_npz_command(
        file_path: FilePath = "./core_trajectories.npz"):  # TODO: Make this a directory and a file and default to local and this name for either if they're not present.
    viewer.view_core(file_path)


@app.command(name="view_npz")
def view_npz_command(npz_path: FilePath = "./core_trajectories.npz"):
    return viewer.collapse_viewer(dir_path=npz_path)


@app.command(name="render")
def render_command(dir_path: FilePath = "./"):
    return viewer.render2(dir_path)


if __name__ == "__main__":
    app()
