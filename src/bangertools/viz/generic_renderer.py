import pickle
import re
from pathlib import Path

import numpy as np
import pynbody

from .common import color_from_temperature


class GenericRenderer:
    POINT_SIZE = 3
    MAX_POINTS = 200_000
    MAX_FRAMES = None

    def __init__(self, dir_path, force_cache=False):

        dir_path = Path(dir_path).resolve()
        cache_file_path = dir_path / f"{dir_path.name}.generic.frames"

        try:
            with open(cache_file_path, 'rb') as fp:
                self.frames = pickle.load(fp)
            if self.frames is None or len(self.frames) == 0 or force_cache:
                raise Exception()
        except Exception as _:
            self.frames = self.load_frames(dir_path)
            with open(cache_file_path, 'wb') as fp:
                pickle.dump(self.frames, fp)

        extent = np.max(np.linalg.norm(self.frames[0]['pos'], axis=1))
        self.distance = extent.real * 2.0

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]
        pos_ = frame['pos']
        color_ = frame['color']

        scatter.set_data(pos_, face_color=color_, size=self.POINT_SIZE)

    def load_frames(self, dir_path):
        frames = []
        snapshot_paths = [
            p.name for p in Path(dir_path).glob(f"*")
            if re.fullmatch(r".*\.\d{6}", p.name)
        ]

        snapshot_paths.sort()

        for idx, file_path in enumerate(snapshot_paths):
            print(f"Loading {file_path}")
            if self.MAX_FRAMES and idx >= self.MAX_FRAMES:
                break

            snapshot = pynbody.load(file_path)

            pos = np.asarray(snapshot["pos"], dtype=np.float32)
            phi = np.asarray(snapshot["phi"], dtype=np.float32)
            center = pos[np.argmin(phi)]
            pos = pos - center

            temp = np.asarray(snapshot["tempEff"], dtype=np.float32)
            color = color_from_temperature(temp)

            frame = {
                "pos": pos,
                "temp": temp,
                "center": center,
                "color": color
            }

            frames.append(frame)

        return frames
