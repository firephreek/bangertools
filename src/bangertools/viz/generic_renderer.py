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

import numpy as np
import pynbody


class FaceOnDensityRenderer(Renderer):

    IMAGE_SIZE = 1024
    WIDTH = "100 kpc"

    def post_process(self):
        pass

    def render_frame(self, frame_number, image_visual):
        image_visual.set_data(
            self.frames[frame_number]["image"]
        )

    def snapshot_to_frame(self, snapshot):

        snapshot.physical_units()

        pynbody.analysis.halo.center(
            snapshot,
            mode="pot"
        )

        try:
            with pynbody.analysis.angmom.faceon(snapshot):
                img = pynbody.plot.image(
                    snapshot.g,
                    width=self.WIDTH,
                    resolution=self.IMAGE_SIZE,
                    noplot=True,
                    log=True,
                )
        except Exception:
            img = pynbody.plot.image(
                snapshot.g,
                width=self.WIDTH,
                resolution=self.IMAGE_SIZE,
                noplot=True,
                log=True,
            )

        img = np.asarray(img, dtype=np.float32)

        return {
            "image": img
        }


class BlackHoleFormationRenderer(Renderer):
    POINT_SIZE = 2
    MAX_POINTS = 150_000

    def post_process(self):
        pass

    def snapshot_to_frame(self, snapshot):
        pos = np.asarray(snapshot.g["pos"], dtype=np.float32)

        phi = np.asarray(snapshot.g["phi"], dtype=np.float32)

        center_idx = np.argmin(phi)
        center = pos[center_idx]

        pos = pos - center

        # Face-on projection:
        # XY plane, ignore Z.
        pos2d = np.zeros_like(pos)
        pos2d[:, 0] = pos[:, 0]
        pos2d[:, 1] = pos[:, 1]

        # Potential well depth
        phi_norm = phi - phi.min()

        p99 = np.percentile(phi_norm, 99)

        phi_norm = np.clip(phi_norm / p99, 0.0, 1.0)

        # Invert so deepest potential -> brightest
        collapse_strength = 1.0 - phi_norm

        color = cm.inferno(collapse_strength)

        # Highlight innermost 0.1%
        threshold = np.percentile(phi, 0.1)

        core_mask = phi <= threshold

        color[core_mask] = np.array(
            [0.2, 0.8, 1.0, 1.0],
            dtype=np.float32
        )

        if len(pos2d) > self.MAX_POINTS:
            weights = collapse_strength + 1e-6

            idx = np.random.choice(
                len(pos2d),
                self.MAX_POINTS,
                replace=False,
                p=weights / weights.sum()
            )

            pos2d = pos2d[idx]
            color = color[idx]

        return {
            "pos": pos2d.astype(np.float32),
            "color": color.astype(np.float32),
            "center": center,
        }

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]

        scatter.set_data(
            frame["pos"],
            face_color=frame["color"],
            size=self.POINT_SIZE,
            edge_color=None
        )


from matplotlib import cm
import numpy as np
import pynbody


class FaceOnGasRenderer(Renderer):
    IMAGE_SIZE = 512
    WIDTH = "100 kpc"
    MAX_PIXELS = None

    def post_process(self):
        pass

    def snapshot_to_frame(self, snapshot):
        snapshot.physical_units()

        h = snapshot.halos()

        with pynbody.analysis.faceon(h[0]):
            img = pynbody.plot.image(
                snapshot.g,
                width=self.WIDTH,
                units="Msol kpc^-2",
                resolution=self.IMAGE_SIZE,
                cmap="bone",
                noplot=True,
                log=True,
            )

        img = np.asarray(img, dtype=np.float32)

        finite = np.isfinite(img)
        vmin = np.percentile(img[finite], 5)
        vmax = np.percentile(img[finite], 99.5)

        img = np.clip((img - vmin) / (vmax - vmin), 0.0, 1.0)

        rgba = cm.bone(img).astype(np.float32)

        ny, nx = img.shape

        x = np.linspace(-1.0, 1.0, nx)
        y = np.linspace(-1.0, 1.0, ny)

        xx, yy = np.meshgrid(x, y)

        pos = np.column_stack([
            xx.ravel(),
            yy.ravel(),
            np.zeros(nx * ny, dtype=np.float32)
        ]).astype(np.float32)

        color = rgba.reshape(-1, 4)

        mask = img.ravel() > 0.01

        pos = pos[mask]
        color = color[mask]

        if self.MAX_PIXELS and len(pos) > self.MAX_PIXELS:
            idx = np.random.choice(
                len(pos),
                self.MAX_PIXELS,
                replace=False
            )
            pos = pos[idx]
            color = color[idx]

        return {
            "pos": pos,
            "color": color
        }

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]

        scatter.set_data(
            frame["pos"],
            face_color=frame["color"],
            edge_color=None,
            size=2,
        )


class GenericRenderer(Renderer):

    def post_process(self):
        pass

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
