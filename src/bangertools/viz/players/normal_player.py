import numpy as np

from .player import TurntablePlayer


class NormalPlayer(TurntablePlayer):

    def __init__(self, frames):
        extent = np.max(np.linalg.norm(frames[0]['pos'], axis=1))
        distance = extent.real * 2.0

        super().__init__(frames, distance=distance)

    def show_frame(self, frame):
        pos_ = frame['pos']
        color_ = frame['color']

        self.scatter.set_data(pos_, face_color=color_, size=3)
