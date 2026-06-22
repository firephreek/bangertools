import numpy as np

from .common import color_from_temperature, Renderer


class CollapseRenderer(Renderer):
    show_trails = True

    def render_frame(self, frame_number, scatter):
        frame = self.frames[frame_number]

        scatter.set_data(
            traj[:, frame, :],
            face_color=(0.2, 0.7, 1.0, 0.8),
            size=4,
        )

        pos = traj[:, frame, :]

        scatter.set_data(
            pos,
            face_color=(0.2, 0.7, 1.0, 0.8),
            size=4,
        )

        if show_trails:

            max_trails = min(len(trail_lines), n_particles)

            for i in range(max_trails):

                trail_lines[i].set_data(
                    traj[i, : frame + 1, :]
                )


    def snapshot_to_frame(self, snapshot):
        pass


class GenericRenderer(Renderer):
    POINT_SIZE = 3
    MAX_POINTS = 200_000
    MAX_FRAMES = None

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
