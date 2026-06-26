import numpy as np
from vispy.scene import visuals

from bangertools.viz.players.player import TurntablePlayer


class CollapseTracerPlayer(TurntablePlayer):

    def setup(self):

        self.trail_visual = visuals.Line()
        self.view.add(self.trail_visual)

        self.traj = self.frames["trajectories"]

        n_particles, n_frames, _ = self.traj.shape

        colors = np.zeros((n_particles, 4), dtype=np.float32)

        colors[:, 0] = 1.0
        colors[:, 1] = 0.85
        colors[:, 2] = 0.1
        colors[:, 3] = 0.9

        # =====================================================
        # CAMERA INIT
        # =====================================================

        all_pos = self.traj.reshape(-1, 3)

        mask = np.isfinite(all_pos[:, 0])

        center = np.nanmean(all_pos[mask], axis=0)

        extent = np.nanmax(
            np.linalg.norm(all_pos[mask] - center, axis=1)
        )

        self.n_particles = n_particles
        self.colors = colors
        self.view.camera.center = center
        self.view.camera.distance = extent * 2.5

    def show_frame(self, frame):

        pos = self.traj[:, frame, :]

        valid = np.isfinite(pos[:, 0])

        self.scatter.set_data(
            pos[valid],
            face_color=self.colors[valid],
            size=6
        )

        # -----------------------------------------
        # Build trail segments
        # -----------------------------------------

        trail_points = []

        trail_start = max(0, frame - 20)

        for p in range(self.n_particles):

            segment = self.traj[p, trail_start:frame + 1]

            good = np.isfinite(segment[:, 0])

            segment = segment[good]

            if len(segment) > 1:
                trail_points.append(segment)

        if trail_points:
            self.trail_visual.set_data(
                pos=np.concatenate(trail_points),
                color=(1, 1, 1, 0.15),
                width=1
            )

        self.canvas.title = (
            f"Core Ancestry Viewer "
            f"| Frame {frame + 1}/{self.n_frames}"
        )
