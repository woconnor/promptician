from rich.progress import Progress, BarColumn

from textual.widgets import Static


class InfiniteLoad(Static):
    """A progress bar that runs forever."""

    DEFAULT_CSS = """
    InfiniteLoad {
        width: auto;
    }
    """

    def __init__(self):
        super().__init__("")
        self.progress = Progress(BarColumn())
        # Add an indeterminate task that will never be completed.
        self.progress.add_task("", total=None)

    def on_mount(self) -> None:
        self.set_interval(1 / 60, self.update_progress_bar)

    def update_progress_bar(self) -> None:
        self.update(self.progress)
