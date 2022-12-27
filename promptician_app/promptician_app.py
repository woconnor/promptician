from textual.app import App, ComposeResult

from .client import Client
from .history import History
from .playground import Playground
from .repository import Repository


class PrompticianApp(App):
    """An app for composing prompts and rating completions."""

    TITLE = "Promptician"

    CSS_PATH = [
        "promptician_app.css",
        "playground.css",
        "history.css",
    ]

    BINDINGS = [
        ("ctrl+t", "toggle_theme", "Toggle theme"),
        ("ctrl+p", "playground", "Playground"),
        ("ctrl+l", "history", "History"),
        ("ctrl+s", "screenshot", "Screenshot"),
        ("ctrl+c,ctrl+q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.client = Client()
        self.repository = Repository()

    def compose(self) -> ComposeResult:
        yield from ()

    def on_mount(self) -> None:
        self.install_screen(Playground(), name="playground")
        self.install_screen(History(), name="history")
        self.push_screen("playground")

    def action_toggle_theme(self) -> None:
        self.dark = not self.dark

    def action_playground(self) -> None:
        self.switch_screen("playground")

    def action_history(self) -> None:
        self.switch_screen("history")


if __name__ == "__main__":
    app = PrompticianApp()
    app.run()
