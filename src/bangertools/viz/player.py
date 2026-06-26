from vispy import app
from vispy.color import Color
from vispy.scene import visuals, SceneCanvas


class Player:

    def __init__(self,
                 frames,
                 canvas,
                 visualizer,
                 fps=20,
                 loop=True,
                 size=(1800, 1000),
                 show=True,
                 keys="interactive",
                 bgcolor=Color('black')
                 ):

        self.fps = fps
        self.loop = loop
        self.playing = None
        self.cur_frame = 0
        self.frames = frames
        self.canvas = canvas
        self.canvas.unfreeze()
        self.canvas.show = show
        self.canvas.bgcolor = bgcolor
        self.canvas.keys = keys
        self.canvas.freeze()
        self.canvas.size = size
        self.visualizer = visualizer

        @canvas.events.mouse_wheel.connect
        def on_scroll(event):
            pass  # Make this change the view box

        @canvas.events.key_press.connect
        def on_key_press(event):
            if event.key == "Space":
                self.playing = not self.playing
            elif event.key in ["L", "l"]:
                self.loop = not self.loop
            else:
                if event.key == "Escape":
                    canvas.close()
                elif event.key == "Right":
                    self.cur_frame = min(self.cur_frame + 1, len(self.frames) - 1)
                elif event.key == "Left":
                    self.cur_frame = max(self.cur_frame - 1, 0)
                elif event.key == "Home":
                    self.cur_frame = 0
                elif event.key == "End":
                    self.cur_frame = len(self.frames) - 1
                self.show_frame(self.cur_frame)

        self.timer = app.Timer(
            interval=1.0 / self.fps,
            connect=lambda event: self.advance(),
            start=True,
        )

        self.print_controls()
        app.run()

    def advance(self):
        if not self.playing:
            return

        if self.cur_frame >= len(self.frames) - 1:
            if self.loop:
                self.cur_frame = 0
            else:
                self.playing = False
                return
        else:
            self.cur_frame += 1

        self.show_frame(self.cur_frame)

    def show_frame(self, frame_number):
        self.visualizer.set_data(self.frames[frame_number])

    def start(self):
        self.playing = True

    @staticmethod
    def print_controls():
        print()
        print("Controls")
        print("--------")
        print("Space  : Play/Pause")
        print("← →    : Frame step")
        print("Home   : First frame")
        print("End    : Last frame")
        print("L      : Loop On/Off")
        print("Mouse  : Rotate")
        print("Wheel  : Zoom")
        print()


class PointPlayer(Player):

    def __init__(self, frames):
        canvas = SceneCanvas(
            keys="interactive",
        )

        view = canvas.central_widget.add_view()
        view.camera.distance = 2.0
        view.camera = "turntable"
        visualizer = visuals.Markers(parent=view.scene)

        super().__init__(frames, canvas, visualizer)


class ImagePlayer:

    def __init__(self, frames, ):
        canvas = SceneCanvas()
        view = canvas.central_widget.add_view()
        first_frame = frames[0]

        self.image = visuals.Image(
            first_frame["image"],
            parent=view.scene,
            cmap="grays"
        )

        view.camera = "panzoom"
        view.camera.aspect = 1

    def show_frame(self, frame_number):
        frame = self.frames[frame_number]

        self.image.set_data(frame["image"])
