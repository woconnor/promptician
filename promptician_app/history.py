from rich.markup import escape

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, ListView, ListItem, Static

from .emoji import EMOJI
from .repository import PromptCompletion


def build_list_item(safeid: str, item: PromptCompletion) -> ListItem:
    text = "".join(
        [
            escape(item.prompt.replace("\n", " ")),
            "[dark_cyan]",
            escape(item.completion.replace("\n", " ")),
            "[/]",
        ]
    )
    return ListItem(
        Static(text),
        Static(EMOJI[item.rating] if item.rating else "", classes="icon"),
        Static(EMOJI["star"] if item.star else "", classes="icon"),
        id=safeid,
    )


class History(Screen):
    """A searchable list of prompt completions."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Container(
                Input(placeholder="Filter by keywords...", id="keywords"),
                Button("Search", variant="primary", id="search"),
                id="search_wrapper",
            ),
            Container(
                ListView(id="results"),
                id="results_wrapper",
            ),
            Container(
                Button("Edit", id="edit"),
                Button("Clone", id="clone"),
                id="actions",
            ),
        )

    def on_mount(self) -> None:
        self.keywords = self.query_one("#keywords")
        self.list_view = self.query_one("#results")
        self.items_by_safeid = {}

    def on_screen_resume(self) -> None:
        # Repopulate on resume as an item may have been changed or added.
        self.populate_list()
        self.list_view.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "keywords":
            self.populate_list()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search":
            self.populate_list()
        elif event.button.id in ["clone", "edit"]:
            self.load_selected_item(event.button.id == "edit")

    # Shows prompt completions that match the search keywords.
    def populate_list(self) -> None:
        self.list_view.query(ListItem).remove()
        self.items_by_safeid = {}

        for item in self.app.repository.items():
            match = True
            for keyword in self.keywords.value.split(" "):
                if keyword not in item.prompt and keyword not in item.completion:
                    match = False
                    break
            if match:
                safeid = f"_{item.id}"  # Prefix with underscore to avoid leading digit
                self.items_by_safeid[safeid] = item
                self.list_view.mount(build_list_item(safeid, item))

        self.list_view.index = 0

    # Opens the playground with the currently selected completion.
    def load_selected_item(self, editable: bool) -> None:
        if self.list_view.index == None:
            return

        safeid = self.list_view.children[self.list_view.index].id
        item = self.items_by_safeid[safeid]

        def load_playground():
            self.app.switch_screen("playground")
            self.app.get_screen("playground").load(item, editable)

        self.app.call_after_refresh(load_playground)
