import typer

import bangertools.lib.viewer as viewer
from bangertools import FilePath
from bangertools.renderers import GenericRenderer

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


