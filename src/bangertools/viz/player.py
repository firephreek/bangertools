from vispy import app
from vispy.color import Color
from vispy.scene import visuals, SceneCanvas


class Player:

    def __init__(self, renderer,
                 fps=20,
                 loop=True,
                 size=(1800, 1000)
                 ):

        canvas = SceneCanvas(
            keys="interactive",
            bgcolor=Color('black'),
            size=size,
            show=True,
        )

        view = canvas.central_widget.add_view()
        view.camera.distance = renderer.distance
        view.camera = "turntable"

        self.fps = fps
        self.loop = loop
        self.playing = None
        self.cur_frame = 0
        self.renderer = renderer
        self.frames = renderer.frames
        self.scatter = visuals.Markers(parent=view.scene)
        self.renderer.render_frame(0, self.scatter)

        def advance():
            if not self.playing:
                return
            if self.loop and self.cur_frame >= len(self.renderer.frames) - 1:
                self.cur_frame = 0
            else:
                self.cur_frame += 1
            self.show_frame(self.cur_frame)

        @canvas.events.key_press.connect
        def on_key_press(event):
            if event.key == "Space":
                self.playing = not self.playing
            else:
                if event.key == "Escape":
                    canvas.close()
                elif event.key == "Right":
                    self.cur_frame = min(self.cur_frame + 1, len(self.renderer.frames) - 1)
                elif event.key == "Left":
                    self.cur_frame = max(self.cur_frame - 1, 0)
                elif event.key == "Home":
                    self.cur_frame = 0
                elif event.key == "End":
                    self.cur_frame = len(self.renderer.frames) - 1
                self.show_frame(self.cur_frame)

        self.timer = app.Timer(
            interval=1.0 / self.fps,
            connect=lambda event: advance(),
            start=True,
        )

        self.print_controls()
        app.run()

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
        print("Mouse  : Rotate")
        print("Wheel  : Zoom")
        print()

    def show_frame(self, frame_number):
        self.renderer.render_frame(frame_number, self.scatter)
