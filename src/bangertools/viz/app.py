import typer

from bangertools import FilePath
from bangertools.viz.players import NormalPlayer, CollapsePlayer
from .generic_renderer import GenericRenderer, CollapseRenderer, FaceOnDensityRenderer

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
    player = NormalPlayer(frames)
    player.start()


@app.command(name="collapse")
def render_traj_command(dir_path: FilePath = "./"):
    print(f"3d Rendering tipsy files in {dir_path}")
    renderer = CollapseRenderer(dir_path)
    player = CollapsePlayer(renderer.frames)
    player.start()


if __name__ == "__main__":
    app()
