import numpy as np

from .common import color_from_temperature, Renderer


class CollapseRenderer(Renderer):
    show_trails = True
    bh_frames = []
    phi_min = []
    core_h2 = []
    core_temp = []

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

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]
        phi = frame['phi']
        pos = frame['pos']
        temp = frame['temp']

        idx = np.argmin(phi)
        center = pos[idx]
        pos = pos - center

        scatter.set_data(
            pos,
            face_color=self.color(temp),
            size=self.POINT_SIZE
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


class GenericRenderer(Renderer):

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]
        pos_ = frame['pos']
        color_ = frame['color']

        scatter.set_data(pos_, face_color=color_, size=self.POINT_SIZE)

    def snapshot_to_frame(self, snapshot):
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

        return frame
