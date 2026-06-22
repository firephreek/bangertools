import pickle
import re
from pathlib import Path

import numpy as np
from matplotlib import cm


class Renderer:

    def __init__(self, dir_path, rebuild_cache=False):

        dir_path = Path(dir_path).resolve()
        cache_file_path = dir_path / f"{dir_path.name}.frames.{self.extension()}"

        try:
            with open(cache_file_path, 'rb') as fp:
                self.frames = pickle.load(fp)
            if self.frames is None or len(self.frames) == 0 or rebuild_cache:
                raise Exception()
        except Exception as _:
            self.frames = self.load_frames(dir_path)
            with open(cache_file_path, 'wb') as fp:
                pickle.dump(self.frames, fp)

        extent = np.max(np.linalg.norm(self.frames[0]['pos'], axis=1))
        self.distance = extent.real * 2.0

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
            frame = self.snapshot_to_frame(snapshot)
            frames.append(frame)

        return frames

    def extension(self):
        return self.__class__.__name__.lower().replace("renderer", "")


def color_from_temperature(temp):
    temp = np.nan_to_num(temp)
    logt = np.log10(np.clip(temp, 1.0, None))
    tmin = np.percentile(logt, 5)
    tmax = np.percentile(logt, 95)

    x = np.clip((logt - tmin) / (tmax - tmin + 1e-12), 0, 1)

    return cm.plasma(x).astype(np.float32)
