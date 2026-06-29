import os

import numpy as np
import pynbody
import typer

from bangertools import FilePath
from bangertools.common import util
from bangertools.viz.players import NormalPlayer, CollapsePlayer
from bangertools.viz.players.collapse_tracer_player import CollapseTracerPlayer
from bangertools.viz.players.dm_player import DMPlayer
from .generic_renderer import GenericRenderer, CollapseRenderer

app = typer.Typer(help="Data visualization commands")


@app.command(name="trace")
def view_collapse_trace(dir_path: FilePath = "./"):
    npz_file = os.path.join(dir_path, "core_trajectories.npz")
    frames = np.load(npz_file)

    player = CollapseTracerPlayer(frames)
    player.start()


def load_frames(dir_path):
    frames = []

    snapshot_paths = util.get_snapshots(dir_path)
    for idx, file_path in enumerate(snapshot_paths):
        file_path = os.path.join(dir_path, file_path)
        frames.append(pynbody.load(file_path))

    return frames


@app.command(name="gas")
def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
    print(f"3d Rendering tipsy files in {dir_path}")

    snapshots = load_frames(dir_path)
    player = DMPlayer(snapshots)
    player.start()


# @app.command(name="gas")
# def view_core_command(dir_path: FilePath = "./"):  # TODO: provide a pattern matching option
#     print(f"3d Rendering tipsy files in {dir_path}")
#     renderer = FaceOnDensityRenderer(dir_path)
#     player = ImagePlayer(renderer)
#     player.start()


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
