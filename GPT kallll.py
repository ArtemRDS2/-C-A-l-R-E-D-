
#FROM ARTEM_RDS2
#FROM ARTEM_RDS2
#FROM ARTEM_RDS2


from kivy.app import App
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Line

#КАСТОМИЗАЦИЯ

BG = "#480101"
BUTTON = "#611414"
CYAN = "#FF0000"
PURPLE = "#BE1A1A"
ORANGE = "#FF4343"
WHITE = "#230202"


def rgba(color):
    return get_color_from_hex(color)


class NeonButton(Button):
    def __init__(self, accent=CYAN, **kwargs):
        self.accent = accent
        self.base_color = rgba(BUTTON)
        self.pressed_color = rgba("#293B5C")
        self.current_scale = 1.0

        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", rgba(WHITE))
        kwargs.setdefault("font_size", dp(23))
        kwargs.setdefault("bold", True)

        super().__init__(**kwargs)

        with self.canvas.before:
            self.fill_color = Color(*self.base_color)
            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(17)]
            )

            self.border_color = Color(*rgba(self.accent))
            self.border_line = Line(
                rounded_rectangle=(
                    self.x, self.y,
                    self.width, self.height,
                    dp(17)
                ),
                width=1.25
            )

        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.bind(on_press=self.animate_press)
        self.bind(on_release=self.animate_release)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

        self.border_line.rounded_rectangle = (
            self.x, self.y,
            self.width, self.height,
            dp(17)
        )

    def animate_press(self, *args):
        Animation.cancel_all(self, "current_scale")
        Animation.cancel_all(self, "opacity")

        Animation(
            current_scale=0.93,
            duration=0.10,
            t="out_quad"
        ).start(self)

        Animation(
            rgba=self.pressed_color,
            duration=0.10
        ).start(self.fill_color)

        Animation(
            rgba=rgba(WHITE),
            duration=0.10
        ).start(self.border_color)

    def animate_release(self, *args):
        Animation.cancel_all(self, "current_scale")

        Animation(
            current_scale=1.0,
            duration=0.28,
            t="out_back"
        ).start(self)

        Animation(
            rgba=self.base_color,
            duration=0.25,
            t="out_quad"
        ).start(self.fill_color)

        Animation(
            rgba=rgba(self.accent),
            duration=0.30,
            t="out_quad"
        ).start(self.border_color)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_origin = touch.pos
        return super().on_touch_down(touch)


class CalculatorApp(App):
    def build(self):
        Window.clearcolor = rgba(BG)
        Window.size = (480, 850)

        self.expression = ""

        main = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(14)
        )

        title = Label(
            text="°º¤ø,¸¸,ø¤º°`°º¤ø,¸C A l R E D¸,ø¤º°`°º¤ø,¸¸,ø¤º°",
            markup=True,
            font_size=dp(20),
            size_hint_y=0.05,
            color=rgba(WHITE)
        )
        main.add_widget(title)

        self.display = Label(
            text="0",
            font_size=dp(40),
            bold=True,
            halign="right",
            valign="middle",
            color=rgba(WHITE),
            size_hint_y=0.23
        )

        self.display.bind(
            size=lambda instance, value:
            setattr(instance, "text_size", value)
        )

        main.add_widget(self.display)

        buttons = [
            ["Del", "Bs", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="]
        ]

        grid = GridLayout(
            cols=4,
            spacing=dp(10),
            size_hint_y=0.65
        )

        for row in buttons:
            for symbol in row:
                accent = (
                    ORANGE if symbol in ["+", "−", "×", "÷", "="]
                    else PURPLE if symbol in ["C", "⌫", "%", "±"]
                    else CYAN
                )

                button = NeonButton(
                    text=symbol,
                    accent=accent
                )

                if symbol == "=":
                    button.base_color = rgba("#800000")
                    button.fill_color.rgba = button.base_color

                button.bind(
                    on_release=lambda instance, s=symbol:
                    self.on_button(s)
                )

                grid.add_widget(button)

        main.add_widget(grid)
        return main

    def on_button(self, symbol):
        if symbol == "Del":
            self.expression = ""

        elif symbol == "Bs":
            self.expression = self.expression[:-1]

        elif symbol == "=":
            try:
                expr = (
                    self.expression
                    .replace("×", "*")
                    .replace("÷", "/")
                    .replace("−", "-")
                )

                allowed = set("0123456789.+-*/() ")

                if not expr or any(c not in allowed for c in expr):
                    raise ValueError

                result = eval(expr, {"__builtins__": {}}, {})

                if not isinstance(result, (int, float)):
                    raise ValueError

                self.expression = (
                    str(int(result))
                    if result == int(result)
                    else str(round(result, 10))
                )

            except (ValueError, SyntaxError, ZeroDivisionError,
                    OverflowError):
                self.expression = "Ошибка"

        elif symbol == "%":
            try:
                expr = (
                    self.expression
                    .replace("×", "*")
                    .replace("÷", "/")
                    .replace("−", "-")
                )

                allowed = set("0123456789.+-*/() ")

                if not expr or any(c not in allowed for c in expr):
                    raise ValueError

                result = eval(expr, {"__builtins__": {}}, {})
                self.expression = str(result / 100)

            except (ValueError, SyntaxError, ZeroDivisionError,
                    OverflowError):
                self.expression = "Ошибка"

        elif symbol == "±":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression

        else:
            if self.expression == "Ошибка":
                self.expression = ""

            operators = ["+", "−", "×", "÷"]

            if symbol in operators:
                if not self.expression:
                    if symbol == "−":
                        self.expression = "-"
                elif self.expression[-1] in operators:
                    self.expression = self.expression[:-1] + symbol
                else:
                    self.expression += symbol
            else:
                self.expression += symbol

        self.display.text = self.expression or "0"


if __name__ == "__main__":
    CalculatorApp().run()