import pickle
from pathlib import Path

import numpy as np
from matplotlib import cm


class Renderer:

    def __init__(self, dir_path, extension, rebuild_cache=False):

        dir_path = Path(dir_path).resolve()
        cache_file_path = dir_path / f"{dir_path.name}.frames.{extension}"

        try:
            with open(cache_file_path, 'rb') as fp:
                self.frames = pickle.load(fp)
            if self.frames is None or len(self.frames) == 0 or rebuild_cache:
                raise Exception()
        except Exception as _:
            self.frames = self.load_frames(dir_path)
            with open(cache_file_path, 'wb') as fp:
                pickle.dump(self.frames, fp)


def color_from_temperature(temp):
    temp = np.nan_to_num(temp)
    logt = np.log10(np.clip(temp, 1.0, None))
    tmin = np.percentile(logt, 5)
    tmax = np.percentile(logt, 95)

    x = np.clip((logt - tmin) / (tmax - tmin + 1e-12), 0, 1)

    return cm.plasma(x).astype(np.float32)
