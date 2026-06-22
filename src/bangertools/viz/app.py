import typer

from bangertools.viz import Player
from bangertools import FilePath
from .generic import GenericRenderer

app = typer.Typer(help="Data visualization commands")

@app.command(name="render")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    renderer = GenericRenderer(dir_path)
    player = Player(renderer)
    player.start()


if __name__ == "__main__":
    app()
