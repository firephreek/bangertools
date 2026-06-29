import os
import re
from pathlib import Path

import numpy as np
import pynbody


class SnapshotRenderer:
    def generate_frames(self, dir_path):
        raise NotImplementedError("Must implement this method in your base class")

    def __init__(self, dir_path, extension, force_rebuild):
        dir_path = Path(dir_path).resolve()
        cache_file_path = dir_path / f"{dir_path.name}.frames.{extension}"

        try:
            data = np.load(f'{cache_file_path}.npz', allow_pickle=True)
            self.frames = data['frames']
            if self.frames is None or len(self.frames) == 0 or force_rebuild:
                raise Exception()
        except Exception as e:
            print(f'{"Re" if force_rebuild else ""}building cache')
            self.frames = self.generate_frames(dir_path)
            np.savez_compressed(cache_file_path, frames=self.frames)

        self.snapshot_paths = [
            os.path.join(dir_path, p.name) for p in Path(dir_path).glob(f"*")
            if re.fullmatch(r".*\.\d{6}", p.name)
        ]

        self.snapshot_paths.sort()


class CoreRenderer(SnapshotRenderer):
    final_core_particles = 1000
    POINT_SIZE = 3
    MAX_POINTS = 200_000
    MAX_FRAMES = None

    def __init__(self, dir_path, rebuild_cache=False):
        super().__init__(dir_path, 'core', force_rebuild=rebuild_cache)

    def generate_frames(self, dir_path):
        frames = []

        for idx, file_path in enumerate(self.snapshot_paths):
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
