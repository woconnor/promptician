from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button


class RadioGroup(Widget):
    """A control that allows at most one child button to be selected"""

    DEFAULT_CSS = """
    RadioGroup {
        layout: horizontal;
        margin: 0;
        padding: 0;
        border: none;
    }
    """

    selected = reactive(None)  # id of selected button, if any

    def watch_selected(self, value: int | None) -> None:
        self.query(Button).remove_class("selected")
        if value != None:
            self.query("#" + value).add_class("selected")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if self.selected != event.button.id:
            self.selected = event.button.id
        else:
            self.selected = None
