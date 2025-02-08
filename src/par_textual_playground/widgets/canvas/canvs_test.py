import rich.color
from textual import on
from textual.app import ComposeResult
from textual.widget import Widget

from par_textual_playground.widgets.canvas.hires import HiResMode
from par_textual_playground.widgets.canvas.par_canvas import ParCanvas


class Ball:
    def __init__(
        self,
        canvas: ParCanvas,
        pos: tuple[float, float],
        velocity: tuple[float, float],
        radius: float = 5,
        color: str = "white",
        filled: bool = True,
    ):
        self.canvas = canvas
        self.pos = pos
        self.velocity = velocity
        self.radius = radius
        self.color = color
        self.filled = filled

    def draw(self, erase: bool = False) -> None:
        if self.filled:
            self.canvas.draw_filled_circle_highres(
                self.pos[0],
                self.pos[1],
                self.radius,
                style="rgb(0,0,0)" if erase else self.color,
            )
        else:
            self.canvas.draw_circle_highres(
                self.pos[0],
                self.pos[1],
                self.radius,
                style="rgb(0,0,0)" if erase else self.color,
            )

    def bounce_walls(self):
        x = self.pos[0]
        y = self.pos[1]
        r = self.radius

        if x-1 <= r or x+1 >= self.canvas.size.width - r:
            self.velocity = (-self.velocity[0], self.velocity[1])
        if y-1 <= r*0.5 or y+1 >= self.canvas.size.height - r*0.5:
            self.velocity = (self.velocity[0], -self.velocity[1])

    def update(self) -> None:
        self.bounce_walls()
        self.pos = (
            self.pos[0] + self.velocity[0],
            self.pos[1] + self.velocity[1],
        )


class CanvasTest(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas = ParCanvas(id="canvas")
        self.canvas.border_title = "Canvas widget border"
        self.ball = Ball(self.canvas,(16, 16), (0.2, 0.2), 10, "red", filled=False)

    def compose(self) -> ComposeResult:
        yield self.canvas

    def on_mount(self) -> None:
        self.call_after_refresh(self.update_size)
        self.set_interval(1 / 60, self.update)

    def update(self) -> None:
        # self.canvas.reset(self.size)
        self.canvas.draw_rectangle_box(0, 0, self.canvas.size.width - 1, self.canvas.size.height - 1, thickness=2)
        self.ball.draw(erase=True)
        self.ball.update()
        self.ball.draw()

    @on(ParCanvas.Resize)
    def update_size(self) -> None:
        canvas = self.canvas
        self.app.set_info(f"Canvas size: {self.size}")
        canvas.reset(self.size)
        canvas.draw_rectangle_box(0, 0, canvas.size.width - 1, canvas.size.height - 1, thickness=2)
        canvas.draw_filled_circle_highres(
            int(canvas.size.width * 0.75), int(canvas.size.height * 0.75), 15, style="white"
        )

        canvas.draw_circle_highres(
            int(canvas.size.width * 0.25),
            int(canvas.size.height * 0.25),
            15,
            hires_mode=HiResMode.HALFBLOCK,
            style="green",
        )
        self.update()
        # canvas.draw_hires_line(
        #     1, 1, canvas.size.width - 2, canvas.size.height - 2, hires_mode=HiResMode.BRAILLE, style="red"
        # )

        canvas.write_text(
            14,
            1,
            "[green]Bresenham's algorithm",
        )
