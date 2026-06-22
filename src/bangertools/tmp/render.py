#!/usr/bin/env python3

"""
collapse_viewer.py

GPU viewer for collapse_trajectories.npz

Controls:
    Space     = play/pause
    Left/Right= step frame
    R         = reset camera
    T         = toggle trails
    Esc       = quit

Mouse:
    Left drag = rotate
    Wheel     = zoom
"""

import numpy as np
from vispy import app, scene
from vispy.scene import visuals

# --------------------------------------------------
# Load trajectory data
# --------------------------------------------------

data = np.load("collapse_trajectories.npz")

particle_ids = data["particle_ids"]
traj = data["trajectories"]

n_particles, n_frames, _ = traj.shape

print(f"Particles : {n_particles}")
print(f"Frames    : {n_frames}")

# --------------------------------------------------
# Viewer state
# --------------------------------------------------

frame = 0
playing = True
show_trails = True

# --------------------------------------------------
# Canvas
# --------------------------------------------------

canvas = scene.SceneCanvas(
    keys="interactive",
    bgcolor="black",
    size=(1600, 900),
    show=True,
)

view = canvas.central_widget.add_view()
view.camera = "turntable"
view.camera.fov = 45

# --------------------------------------------------
# Initial positions
# --------------------------------------------------

current = traj[:, 0, :]

scatter = visuals.Markers(
    parent=view.scene
)

scatter.set_data(
    current,
    face_color=(0.2, 0.7, 1.0, 0.8),
    size=4,
)

# --------------------------------------------------
# Trails
# --------------------------------------------------

trail_lines = []

if show_trails:

    for i in range(min(n_particles, 2000)):
        line = visuals.Line(
            pos=traj[i, :1, :],
            color=(1, 1, 1, 0.15),
            width=1,
            parent=view.scene,
        )

        trail_lines.append(line)

# --------------------------------------------------
# Camera setup
# --------------------------------------------------

all_pos = traj.reshape(-1, 3)

valid = np.isfinite(all_pos[:, 0])

center = np.nanmean(all_pos[valid], axis=0)

extent = np.nanmax(
    np.linalg.norm(
        all_pos[valid] - center,
        axis=1
    )
)

view.camera.center = center
view.camera.distance = extent * 3

# --------------------------------------------------
# Update frame
# --------------------------------------------------

def update(event):

    global frame

    if not playing:
        return

    frame += 1

    if frame >= n_frames:
        frame = 0

    pos = traj[:, frame, :]

    scatter.set_data(
        pos,
        face_color=(0.2, 0.7, 1.0, 0.8),
        size=4,
    )

    if show_trails:

        max_trails = min(len(trail_lines), n_particles)

        for i in range(max_trails):

            trail_lines[i].set_data(
                traj[i, : frame + 1, :]
            )

# --------------------------------------------------
# Keyboard
# --------------------------------------------------

@canvas.events.key_press.connect
def on_key(event):

    global playing
    global frame

    if event.key == "Space":
        playing = not playing

    elif event.key == "Right":

        frame = min(frame + 1, n_frames - 1)

        scatter.set_data(
            traj[:, frame, :],
            face_color=(0.2, 0.7, 1.0, 0.8),
            size=4,
        )

    elif event.key == "Left":

        frame = max(frame - 1, 0)

        scatter.set_data(
            traj[:, frame, :],
            face_color=(0.2, 0.7, 1.0, 0.8),
            size=4,
        )

    elif event.key == "R":

        view.camera.center = center
        view.camera.distance = extent * 3

    elif event.key == "Escape":

        canvas.close()

# --------------------------------------------------
# Timer
# --------------------------------------------------

timer = app.Timer(
    interval=1/30,
    connect=update,
    start=True,
)

app.run()
