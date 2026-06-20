global frame


def collapse_viewer(dir_path: str):
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

    data = np.load(dir_path)

    particle_ids = data["particle_ids"]
    traj = data["trajectories"]

    n_particles, n_frames, _ = traj.shape

    print(f"Particles : {n_particles}")
    print(f"Frames    : {n_frames}")

    # --------------------------------------------------
    # Viewer state
    # --------------------------------------------------

    global frame
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
        print("Loading Trails...")
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
        interval=1 / 30,
        connect=update,
        start=True,
    )

    app.run()


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


def render2(dir_path: str):
    import re
    from pathlib import Path

    import numpy as np
    import pynbody

    from vispy import app
    from vispy.scene import visuals
    app.use_app('PyQt6')
    from vispy import scene
    # =====================================================
    # CONFIG
    # =====================================================

    SNAP_PREFIX = "o9M_1."
    POINT_SIZE = 3
    FPS = 20

    # downsample if desired
    MAX_POINTS = 200000

    # =====================================================
    # FIND SNAPSHOTS
    # =====================================================

    snapshots = []

    for f in Path(dir_path).glob(f"{SNAP_PREFIX}*"):
        if re.fullmatch(r"o9M_1\.\d+", f.name):
            snapshots.append(str(f))

    snapshots.sort()

    if not snapshots:
        raise RuntimeError("No snapshots found")

    print("Found", len(snapshots), "snapshots")

    # =====================================================
    # LOAD SNAPSHOT
    # =====================================================

    cache = {}

    def load_frame(i):
        if i in cache:
            return cache[i]

        s = pynbody.load(snapshots[i])

        pos = np.asarray(s["pos"], dtype=np.float32)

        if len(pos) > MAX_POINTS:
            idx = np.random.choice(
                len(pos),
                MAX_POINTS,
                replace=False
            )

            pos = pos[idx]

            temp = np.asarray(
                s["tempEff"],
                dtype=np.float32
            )[idx]

            phi = np.asarray(
                s["phi"],
                dtype=np.float32
            )[idx]

        else:
            temp = np.asarray(
                s["tempEff"],
                dtype=np.float32
            )
            phi = np.asarray(
                s["phi"],
                dtype=np.float32
            )

        center_idx = np.argmin(phi)
        center = pos[center_idx]
        pos = pos - center

        cache[i] = (
            pos,
            temp,
            center
        )

        return cache[i]

    # =====================================================
    # COLORMAP
    # =====================================================

    from matplotlib import cm

    def color_from_temperature(temp):
        temp = np.nan_to_num(temp)
        logt = np.log10(np.clip(temp, 1.0, None))
        tmin = np.percentile(logt, 5)
        tmax = np.percentile(logt, 95)

        x = np.clip((logt - tmin) / (tmax - tmin + 1e-12), 0, 1)

        return cm.plasma(x).astype(np.float32)

    # =====================================================
    # CANVAS
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
    # INITIAL FRAME
    # =====================================================

    frame = 0
    playing = True

    pos, temp, center = load_frame(frame)

    colors = color_from_temperature(temp)

    scatter = visuals.Markers(
        parent=view.scene
    )

    scatter.set_data(
        pos,
        face_color=colors,
        size=POINT_SIZE
    )

    extent = np.max(
        np.linalg.norm(pos, axis=1)
    )

    view.camera.distance = extent * 2

    # =====================================================
    # UPDATE
    # =====================================================

    def redraw():
        pos, temp, center = load_frame(frame)

        scatter.set_data(
            pos,
            face_color=color_from_temperature(temp),
            size=POINT_SIZE
        )

    def advance(event):
        global frame

        if not playing:
            return

        frame += 1

        if frame >= len(snapshots):
            frame = 0

        redraw()

    # =====================================================
    # KEYS
    # =====================================================

    @canvas.events.key_press.connect
    def on_key(event):
        global frame
        global playing

        if event.key == "Space":
            playing = not playing

        elif event.key == "Right":

            frame = min(
                frame + 1,
                len(snapshots) - 1
            )

            redraw()

        elif event.key == "Left":

            frame = max(
                frame - 1,
                0
            )

            redraw()

        elif event.key == "Home":

            frame = 0
            redraw()

        elif event.key == "End":

            frame = len(snapshots) - 1
            redraw()

        elif event.key == "Escape":

            canvas.close()

    # =====================================================
    # TIMER
    # =====================================================

    timer = app.Timer(
        interval=1.0 / FPS,
        connect=advance,
        start=True,
    )

    print()
    print("Controls")
    print("--------")
    print("Space  : Play/Pause")
    print("← →    : Frame step")
    print("Home   : First frame")
    print("End    : Last frame")
    print("Mouse  : Rotate")
    print("Wheel  : Zoom")
    print()

    app.run()
