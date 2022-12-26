from textual.reactive import reactive
from textual.widgets import Static


PAUSE_CHARACTERS = {" ", ",", ".", ";", ":", "!", "?", "\n"}
CURSOR = "█"


class Ghostwriter(Static):
    """Renders text one character at a time, with pauses after punctuation."""

    value = reactive("")
    index = reactive(0)

    def watch_value(self, value: str) -> None:
        self.index = 0
        self.pause = 0
        self.update("")
        self.timer.resume()

    def on_mount(self) -> None:
        self.timer = self.set_interval(1 / 40, self.advance)
        self.timer.pause()

    def advance(self) -> None:
        if self.index < len(self.value):
            if self.pause > 0:
                self.pause -= 1
            else:
                c = self.value[self.index]
                if c in PAUSE_CHARACTERS:
                    self.pause = 5
                self.index += 1
                self.update(self.value[: self.index] + CURSOR)
        else:
            self.update(self.value)
            self.timer.pause()
