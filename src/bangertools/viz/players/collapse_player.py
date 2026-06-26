import numpy as np
from vispy.scene import SceneCanvas, visuals

from .player import Player


class CollapsePlayer(Player):

    def __init__(self, frames):
        canvas = SceneCanvas()
        view = canvas.central_widget.add_view()
        view.camera.distance = 2.0
        view.camera = "turntable"
        self.scatter = visuals.Markers(parent=view.scene)

        super().__init__(frames, canvas)

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
