import numpy as np
from vispy.scene import SceneCanvas, visuals

from .player import Player


class NormalPlayer(Player):

    def __init__(self, frames):
        canvas = SceneCanvas()
        view = canvas.central_widget.add_view()
        view.camera.distance = 2.0
        view.camera = "turntable"

        self.scatter = visuals.Markers(parent=view.scene)
        extent = np.max(np.linalg.norm(frames[0]['pos'], axis=1))
        self.distance = extent.real * 2.0

        super().__init__(frames, canvas)

    def show_frame(self, frame):
        pos_ = frame['pos']
        color_ = frame['color']

        self.scatter.set_data(pos_, face_color=color_, size=3)
