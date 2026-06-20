import typer

from bangertools import FilePath

app = typer.Typer(help="Data visualization commands")


@app.command(name="npz")
def view_core_command(
        file_path: FilePath = "./core_trajectories.npz"):  # TODO: Make this a directory and a file and default to local and this name for either if they're not present.
    from bangertools.lib.core import view_core
    view_core(file_path)


@app.command(name="render")
def render_command(mode: int, dir_path: str, npz_path="./core_trajectories.npz"):
    import bangertools.lib.viewer as viewer

    match mode:
        case 1:
            return viewer.collapse_viewer(dir_path=npz_path),
        case 2:
            return viewer.render2(dir_path)
        case _:
            print("unrecognized mode")


if __name__ == "__main__":
    app()
