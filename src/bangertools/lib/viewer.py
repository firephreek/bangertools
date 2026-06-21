import time

import numpy as np
import pynbody
from matplotlib import cm
from vispy import app
from vispy.color import Color
from vispy.scene import visuals, SceneCanvas


def color_from_temperature(temp):
    # TODO: Consider memoizing this?
    temp = np.nan_to_num(temp)
    logt = np.log10(np.clip(temp, 1.0, None))
    tmin = np.percentile(logt, 5)
    tmax = np.percentile(logt, 95)

    x = np.clip((logt - tmin) / (tmax - tmin + 1e-12), 0, 1)

    return cm.plasma(x).astype(np.float32)


class Player:
    frames = []
    cur_frame = 0

    def start(self):
        self.playing = True

    def close(self):
        self.canvas.close()

    def __process_frame(self, file_path):  # TODO: Could this be threaded?
        # TODO: Print status/state while frames are being loaded
        # TODO: Cache/serialize and save to avoid reprocessing?
        start_time = time.time()
        print(f"Loading {file_path}")
        s = pynbody.load(file_path)
        print(f"Loaded {file_path} in {time.time() - start_time}")

        pos = np.asarray(s["pos"], dtype=np.float32)

        if len(pos) > self.MAX_POINTS:
            idx = np.random.choice(len(pos), self.MAX_POINTS, replace=False)

            pos = pos[idx]

            temp = np.asarray(s["tempEff"], dtype=np.float32)[idx]
            phi = np.asarray(s["phi"], dtype=np.float32)[idx]
        else:
            temp = np.asarray(s["tempEff"], dtype=np.float32)
            phi = np.asarray(s["phi"], dtype=np.float32)

        center_idx = np.argmin(phi)
        center = pos[center_idx]
        pos = pos - center

        frame = (pos, temp, center)

        return frame

    def __cache_frames(self, file_paths: list[str]):
        # TODO: Let's create a pickle file with prefixes and keys, and then we only add frames we need to the
        #  rest we load from the pickle?
        frame_cache = []
        snapshot_paths = []

        for f in file_paths:
            snapshot_paths.append(str(f))

        snapshot_paths.sort()

        for idx, snapshot in enumerate(snapshot_paths):
            frame_cache.append(self.__process_frame(snapshot))

        return frame_cache

    def __redraw(self):
        pos, temp, center = self.frames[self.cur_frame]
        color = color_from_temperature(temp)
        self.scatter.set_data(pos, face_color=color, size=self.POINT_SIZE)

    def advance(self, event):
        if not self.playing:
            return

        self.cur_frame += 1

        if self.AUTO_LOOP and self.cur_frame >= len(self.frames):
            self.cur_frame = 0

        self.__redraw()

    def on_key_press(self, event):
        if event.key == "Space":
            self.playing = not self.playing
        elif event.key == "Right":
            self.cur_frame = min(self.cur_frame + 1, len(self.frames) - 1)
            self.__redraw()
        elif event.key == "Left":
            self.cur_frame = max(self.cur_frame - 1, 0)
            self.__redraw()
        elif event.key == "Home":
            self.cur_frame = 0
            self.__redraw()
        elif event.key == "End":
            self.cur_frame = len(self.frames) - 1
            self.__redraw()
        elif event.key == "Escape":
            self.close()

    def __init__(self, file_paths: list[str],
                 auto_start=False,
                 point_size=3,
                 size=(1800, 1000)
                 ):
        self.AUTO_LOOP = True
        self.playing = None
        self.FPS = 20
        self.MAX_POINTS = 200_000
        self.POINT_SIZE = point_size
        self.frames = self.__cache_frames(file_paths)  # TODO: how to determine the prefix automatically?
        self.cur_frame = 0

        self.canvas = SceneCanvas(
            keys="interactive",
            bgcolor=Color('black'),
            size=size,
            show=True,
        )

        self.view = self.canvas.central_widget.add_view()
        self.view.camera = "turntable"
        pos, temp, center = self.frames[0]
        colors = color_from_temperature(temp)
        self.scatter = visuals.Markers(parent=self.view.scene)
        self.scatter.set_data(pos, face_color=colors, size=self.POINT_SIZE)

        extent = np.max(np.linalg.norm(pos, axis=1))
        self.view.camera.distance = extent.real * 2.0

        self.canvas.connect(self.on_key_press)
        self.timer = app.Timer(
            interval=1.0 / self.FPS,
            connect=self.advance,
            start=True,
        )

        self.print_controls()
        app.run()

    @staticmethod
    def print_controls():
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
