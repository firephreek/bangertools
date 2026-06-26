import numpy as np
from vispy.scene import SceneCanvas, visuals

from .player import Player


class CollapsePlayer(Player):
    show_trails = True
    bh_frames = []
    phi_min = []
    core_h2 = []
    core_temp = []

    def __init__(self, frames):
        canvas = SceneCanvas()
        view = canvas.central_widget.add_view()
        view.camera.distance = 2.0
        view.camera = "turntable"
        self.scatter = visuals.Markers(parent=view.scene)

        super().__init__(frames, canvas)

    def post_process(self):
        for frame in self.frames:
            phi = frame['phi']
            pos = frame['pos']
            temp = frame['temp']
            h2 = frame['h2']

            idx = np.argmin(phi)
            center = pos[idx]
            pos = pos - center
            idx = np.argmin(phi)
            center = pos[idx]
            r = np.linalg.norm(pos - center, axis=1)
            core = r < np.percentile(r, 1)

            self.phi_min.append(phi[idx])
            self.core_h2.append(np.mean(h2[core]))
            self.core_temp.append(np.mean(temp[core]))

        dphi = np.gradient(self.phi_min)

        where = np.where((self.phi_min == np.min(self.phi_min)) & (np.abs(dphi) < np.percentile(np.abs(dphi), 10)))
        bh_candidates = where[0]

        bh_frame = int(bh_candidates[0]) if len(bh_candidates) else np.argmin(self.phi_min)
        self.bh_frames.append(bh_frame)

    def show_frame(self, frame):
        phi = frame['phi']
        pos = frame['pos']
        temp = frame['temp']

        idx = np.argmin(phi)
        center = pos[idx]
        pos = pos - center

        self.scatter.set_data(
            pos,
            face_color=self.color(temp),
            size=3
        )

    def snapshot_to_frame(self, snapshot):
        pos = np.asarray(snapshot["pos"], dtype="float32")
        temp = np.asarray(snapshot["tempEff"], dtype="float32")
        phi = np.asarray(snapshot["phi"], dtype="float32")
        h2 = np.asarray(snapshot.get("H2", np.zeros(len(pos))), dtype="float32")

        return {'pos': pos, 'temp': temp, 'phi': phi, 'h2': h2}

    def color(self, temp):
        temp = np.nan_to_num(temp)

        # log scaling (critical for astrophysics data)
        logt = np.log10(np.clip(temp, 1e-3, None))

        # percentile stretch (prevents outliers ruining contrast)
        vmin, vmax = np.percentile(logt, [2, 98])

        x = (logt - vmin) / (vmax - vmin + 1e-12)

        # nonlinear boost (makes mid-range differences visible)
        x = np.clip(x, 0, 1)
        x = x ** 0.6  # <--- key contrast boost

        # high contrast "fire–ice" mapping
        c = np.zeros((len(temp), 4), dtype="float32")

        c[:, 0] = x ** 1.5  # red (hot core)
        c[:, 1] = (1 - x) * x  # green (mid structure)
        c[:, 2] = (1 - x) ** 1.2  # blue (cold gas)
        c[:, 3] = 0.9

        return c
