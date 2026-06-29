import numpy as np
import pynbody
from vispy.color import Color
from vispy.scene import SceneCanvas, PanZoomCamera
from vispy.scene.visuals import Image

from bangertools.viz.players.player import Player


class DMPlayer(Player):

    def __init__(
            self,
            snapshots,
            qty='rho',
            width="20 kpc",
            units="Msol kpc^-2",
            cmap="magma",
            log=True,
            vmin=None,
            vmax=None,
            resolution=800,
            **kwargs
    ):

        self.qty = qty
        self.width = width
        self.units = units
        self.cmap = cmap
        self.log = log
        self.vmin = vmin
        self.vmax = vmax
        self.resolution = resolution

        # Precompute frames as images
        self.frames = [
            self._render_frame(snap) for snap in snapshots
        ]

        canvas = SceneCanvas(
            keys="interactive",
            size=(1200, 900),
            show=True,
            bgcolor=Color("black")
        )

        self.canvas = canvas
        self.view = canvas.central_widget.add_view()
        self.view.camera = PanZoomCamera(aspect=1)
        self.img = None
        super().__init__(
            frames=self.frames,
            canvas=canvas,
            **kwargs
        )

    def _render_frame(self, snap):

        snap.physical_units()

        img = pynbody.plot.sph.image(
            snap.gas,
            self.qty,
            width=self.width,
            units=self.units,
            log=self.log,
            color="bone",
            vmin=self.vmin,
            vmax=self.vmax,
            noplot=True,
            resolution=self.resolution
        )

        img = np.asarray(img)

        print("frame:", type(img), img.shape)

        return img

    def show_frame(self, frame):

        frame = np.asarray(frame).astype(np.float32)

        if self.img is None:
            self.img = Image(
                frame,
                parent=self.view.scene
            )

            h, w = frame.shape
            self.view.camera.rect = (0, 0, w, h)

        else:
            self.img.set_data(frame)

        self.canvas.update()
