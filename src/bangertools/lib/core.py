#!/usr/bin/env python3

"""
extract_core_history.py

Find particles that end up in the final collapsed core and
track them backward through all snapshots.

Outputs:
    core_particle_ids.npy
    core_trajectories.npz

Trajectory shape:
    (n_particles, n_snapshots, 3)
"""


def build_core(file_path: str, snapshot_prefix="o9M_1.*"):
    import re
    from pathlib import Path
    import numpy as np
    import pynbody

    # =====================================================
    # CONFIG
    # =====================================================

    FINAL_CORE_PARTICLES = 1000
    SNAP_PATTERN = r"o9M_1\.\d+"

    # =====================================================
    # FIND SNAPSHOTS
    # =====================================================

    snapshots = sorted(
        str(f)
        for f in Path(file_path).glob(snapshot_prefix)
        if re.fullmatch(SNAP_PATTERN, f.name)
    )

    if not snapshots:
        raise RuntimeError("No snapshots found")

    print(f"Found {len(snapshots)} snapshots")

    # =====================================================
    # FINAL SNAPSHOT
    # =====================================================

    final_snap = snapshots[-1]

    print(f"Loading final snapshot: {final_snap}")

    s = pynbody.load(final_snap)

    pos = np.asarray(s["pos"])
    phi = np.asarray(s["phi"])
    iord = np.asarray(s["iord"])

    # deepest potential particle
    core_idx = np.argmin(phi)

    core_center = pos[core_idx]

    print("Core center particle:")
    print(f"  ID  = {iord[core_idx]}")
    print(f"  phi = {phi[core_idx]}")

    # distance from core center
    r = np.linalg.norm(pos - core_center, axis=1)

    # nearest N particles
    nearest = np.argsort(r)[:FINAL_CORE_PARTICLES]

    core_ids = iord[nearest]

    print()
    print(f"Selected {len(core_ids)} final-core particles")

    np.save("core_particle_ids.npy", core_ids)

    # =====================================================
    # BUILD TRAJECTORIES
    # =====================================================

    core_set = set(map(int, core_ids))

    traj = []

    for snap_index, snapfile in enumerate(snapshots):

        print(
            f"[{snap_index + 1}/{len(snapshots)}] "
            f"{Path(snapfile).name}"
        )

        s = pynbody.load(snapfile)

        ids = np.asarray(s["iord"])
        pos = np.asarray(s["pos"])

        # map particle ID -> index for only core particles
        id_to_idx = {
            int(pid): idx
            for idx, pid in enumerate(ids)
            if int(pid) in core_set
        }

        frame_positions = np.full(
            (len(core_ids), 3),
            np.nan,
            dtype=np.float32,
        )

        for j, pid in enumerate(core_ids):

            idx = id_to_idx.get(int(pid))

            if idx is not None:
                frame_positions[j] = pos[idx]

        traj.append(frame_positions)

    traj = np.stack(traj, axis=1)

    print()
    print("Trajectory array shape:", traj.shape)
    print("(particles, snapshots, xyz)")

    # =====================================================
    # SAVE
    # =====================================================

    np.savez_compressed(
        "core_trajectories.npz",
        particle_ids=core_ids,
        trajectories=traj,
        snapshots=np.array(snapshots),
    )

    print()
    print("Saved:")
    print("  core_particle_ids.npy")
    print("  core_trajectories.npz")


def view_core(core_file):
    import numpy as np
    from vispy import app, scene
    from vispy.scene import visuals

    # =====================================================
    # LOAD TRAJECTORIES
    # =====================================================

    data = np.load(core_file)

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

            segment = traj[p, trail_start:f + 1]

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
            f"| Frame {f + 1}/{n_frames}"
        )

    # =====================================================
    # FRAME CONTROL
    # =====================================================

    def set_frame(f):

        global frame

        frame = max(
            0,
            min(n_frames - 1, f)
        )

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
        interval=1 / 20,
        connect=advance,
        start=True
    )

    app.run()
