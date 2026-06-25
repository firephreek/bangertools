#!/usr/bin/env python3

import numpy as np
from vispy import app, scene
from vispy.scene import visuals

# =====================================================
# LOAD TRAJECTORIES
# =====================================================

data = np.load("core_trajectories.npz")

traj = data["trajectories"]

n_particles, n_frames, _ = traj.shape

print("Particles:", n_particles)
print("Frames:", n_frames)

# =====================================================
# VISPY
# =====================================================

canvas = scene.SceneCanvas(
    keys="interactive",
    bgcolor="black",
    size=(1800, 1000),
    show=True,
)

view = canvas.central_widget.add_view()
view.camera = "turntable"

# =====================================================
# STATE
# =====================================================

frame = 0
playing = False

# =====================================================
# PARTICLES
# =====================================================

scatter = visuals.Markers()
view.add(scatter)

# =====================================================
# TRAILS
# =====================================================

trail_visual = visuals.Line()
view.add(trail_visual)

# =====================================================
# COLORS
# =====================================================

colors = np.zeros((n_particles, 4), dtype=np.float32)

colors[:, 0] = 1.0
colors[:, 1] = 0.85
colors[:, 2] = 0.1
colors[:, 3] = 0.9

# =====================================================
# CAMERA INIT
# =====================================================

all_pos = traj.reshape(-1, 3)

mask = np.isfinite(all_pos[:, 0])

center = np.nanmean(all_pos[mask], axis=0)

extent = np.nanmax(
    np.linalg.norm(all_pos[mask] - center, axis=1)
)

view.camera.center = center
view.camera.distance = extent * 2.5

# =====================================================
# RENDER
# =====================================================

def render(f):

    pos = traj[:, f, :]

    valid = np.isfinite(pos[:, 0])

    scatter.set_data(
        pos[valid],
        face_color=colors[valid],
        size=6
    )

    # -----------------------------------------
    # Build trail segments
    # -----------------------------------------

    trail_points = []

    trail_start = max(0, f - 20)

    for p in range(n_particles):

        segment = traj[p, trail_start:f+1]

        good = np.isfinite(segment[:, 0])

        segment = segment[good]

        if len(segment) > 1:
            trail_points.append(segment)

    if trail_points:

        trail_visual.set_data(
            pos=np.concatenate(trail_points),
            color=(1, 1, 1, 0.15),
            width=1
        )

    canvas.title = (
        f"Core Ancestry Viewer "
        f"| Frame {f+1}/{n_frames}"
    )

# =====================================================
# FRAME CONTROL
# =====================================================

def set_frame(f):

    global frame
    if f >= n_frames:
        f = 0
    elif f < 0:
        f = n_frames

    frame = max(
        0,
        min(n_frames - 1, f)
    )

    if frame >= n_frames:
        frame = 0

    render(frame)

    canvas.update()

# =====================================================
# INITIAL DRAW
# =====================================================

set_frame(0)

# =====================================================
# PLAYBACK
# =====================================================

def advance(event):

    if not playing:
        return

    set_frame(frame + 1)

# =====================================================
# SCROLL SCRUB
# =====================================================

@canvas.events.mouse_wheel.connect
def on_scroll(event):

    delta = int(event.delta[1])

    set_frame(frame + delta)

# =====================================================
# KEYS
# =====================================================

@canvas.events.key_press.connect
def on_key(event):

    global playing

    if event.key == "Space":
        playing = not playing

    elif event.key == "Right":
        set_frame(frame + 1)

    elif event.key == "Left":
        set_frame(frame - 1)

    elif event.key == "Home":
        set_frame(0)

    elif event.key == "End":
        set_frame(n_frames - 1)

    elif event.key == "Escape":
        canvas.close()

# =====================================================
# TIMER
# =====================================================

timer = app.Timer(
    interval=1/20,
    connect=advance,
    start=True
)

app.run()
