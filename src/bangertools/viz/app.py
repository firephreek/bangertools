import typer

from bangertools import FilePath
from .generic_renderer import GenericRenderer, CollapseRenderer, FaceOnDensityRenderer
from .player import Player, ImagePlayer, PointPlayer

app = typer.Typer(help="Data visualization commands")


@app.command(name="gas")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    print(f"3d Rendering tipsy files in {dir_path}")
    renderer = FaceOnDensityRenderer(dir_path)
    player = ImagePlayer(renderer)
    player.start()

@app.command(name="render")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    print(f"3d Rendering tipsy files in {dir_path}")
    renderer = GenericRenderer(dir_path)
    frames = renderer.frames
    player = PointPlayer(frames)
    player.start()

@app.command(name="collapse")
def render_traj_command(dir_path:FilePath="./"):
    print(f"3d Rendering tipsy files in {dir_path}")
    renderer = CollapseRenderer(dir_path)
    player = PointPlayer(renderer)
    player.start()


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



if __name__ == "__main__":
    app()
