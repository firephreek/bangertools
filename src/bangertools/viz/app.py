import typer

from bangertools import FilePath
from .player import Player
from .generic_renderer import GenericRenderer

app = typer.Typer(help="Data visualization commands")

@app.command(name="render")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    print(f"3d Rendering tipsy files in {dir_path}")
    renderer = GenericRenderer(dir_path)
    player = Player(renderer)
    player.start()


if __name__ == "__main__":
    app()
