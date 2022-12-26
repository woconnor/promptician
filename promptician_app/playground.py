import asyncio

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static

from .client import CompletionRequest, CompletionResult
from .emoji import EMOJI
from .ghostwriter import Ghostwriter
from .infinite_load import InfiniteLoad
from .radio_group import RadioGroup
from .repository import PromptCompletion


def escape(text: str) -> str:
    return text.replace("\n", "\\n")


def unescape(text: str) -> str:
    return text.replace("\\n", "\n")


def set_input(input: Input, value: str) -> None:
    input.value = value
    input.view_position = 0  # Textual bug? First character hidden without setting this.


class Playground(Screen):
    """A playground for composing prompts and rating completions."""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Container(
                Static("Model", classes="label"),
                Input(placeholder="Model name", id="model"),
                Static("Temperature", classes="label"),
                Input(placeholder="Randomness", id="temperature"),
                Static("Stop words", classes="label"),
                Input(placeholder="Halt on word", id="stop_words"),
                Static("Max response", classes="label"),
                Input(placeholder="Number of tokens", id="max_tokens"),
                id="parameters",
            ),
            Button("Reset", id="reset"),
            id="settings",
        )
        yield Container(
            Input(placeholder="Once upon a time,", id="prompt"),
            Button("Run", variant="primary", id="run"),
            id="prompt_wrapper",
        )
        yield Container(
            Ghostwriter(id="ghostwriter"),
            id="output",
        )
        yield Container(
            Static(),
            RadioGroup(
                Button(EMOJI["negative"], id="negative"),
                Button(EMOJI["neutral"], id="neutral"),
                Button(EMOJI["positive"], id="positive"),
                id="rating_group",
            ),
            RadioGroup(
                Button(EMOJI["star"], id="star"),
                id="star_group",
            ),
            id="evaluation",
        )

    def on_mount(self) -> None:
        # Find mounted widgets for later convenience.
        self.prompt = self.query_one("#prompt")
        self.model = self.query_one("#model")
        self.temperature = self.query_one("#temperature")
        self.max_tokens = self.query_one("#max_tokens")
        self.stop_words = self.query_one("#stop_words")
        self.output = self.query_one("#output")
        self.ghostwriter = self.query_one("#ghostwriter")
        self.evaluation = self.query_one("#evaluation")
        self.rating = self.query_one("#rating_group")
        self.star = self.query_one("#star_group")
        # Set initial values.
        self.reset()

    def on_screen_resume(self) -> None:
        self.prompt.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "prompt":
            asyncio.create_task(self.new_completion())

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            asyncio.create_task(self.new_completion())
        elif event.button.id == "reset":
            self.reset()
        elif event.button.id in ["negative", "neutral", "positive", "star"]:
            self.save()

    # Requests a new completion for the prompt and persists the result.
    async def new_completion(self) -> None:
        self.reset_output(spinner=True)
        self.reset_evaluation()
        try:
            self.result = await self.app.client.complete(self.to_request())
            self.reset_output(self.result.completion, ghostwrite=True)
            self.reset_evaluation(enabled=True)
            self.save()
        except Exception as err:
            print(err)
            self.reset_output(f"Unexpected {err=}, {type(err)=}")

    # Restores state from previous completion.
    def load(self, item: PromptCompletion, editable: bool) -> None:
        self.reset_input(
            prompt=item.prompt,
            model=item.raw_request["model"],
            temperature=item.raw_request["temperature"],
            stop_words=item.raw_request["stop"],
            max_tokens=item.raw_request["max_tokens"],
        )

        if editable:
            self.result = CompletionResult(
                id=item.id,
                completion=item.completion,
                raw_request=item.raw_request,
                raw_response=item.raw_response,
            )
            self.reset_output(item.completion)
            self.reset_evaluation(rating=item.rating, star=item.star, enabled=True)
        else:
            self.result = None
            self.reset_output()
            self.reset_evaluation()

    # Upserts the current completion.
    def save(self) -> None:
        try:
            if self.result != None:
                self.app.repository.upsert(
                    PromptCompletion(
                        id=self.result.id,
                        prompt=unescape(self.prompt.value),
                        completion=self.result.completion,
                        rating=self.rating.selected,
                        star=bool(self.star.selected),
                        raw_request=self.result.raw_request,
                        raw_response=self.result.raw_response,
                    )
                )
        except Exception as err:
            print(err)
            self.reset_output(f"Unexpected {err=}, {type(err)=}")

    # Clears the state to a fresh prompt, restoring all defaults.
    def reset(self) -> None:
        self.result = None
        self.reset_input()
        self.reset_output()
        self.reset_evaluation()

    def reset_input(
        self,
        prompt: str = "",
        model: str = "text-davinci-003",
        temperature: float = 0.7,
        stop_words: list[str] | None = None,
        max_tokens: int = 256,
    ) -> None:
        set_input(self.prompt, escape(prompt))
        set_input(self.model, model)
        set_input(self.temperature, str(temperature))
        set_input(self.stop_words, escape(" ".join(stop_words or [])))
        set_input(self.max_tokens, str(max_tokens))

    def reset_output(
        self, text: str = "", ghostwrite: bool = False, spinner: bool = False
    ) -> None:
        if spinner and not self.query("#loading"):
            self.mount(Container(InfiniteLoad(), id="loading"), before=self.output)
        elif not spinner:
            self.query("#loading").remove()

        self.ghostwriter.value = text
        self.ghostwriter.index = 0 if ghostwrite else len(text)

    def reset_evaluation(
        self,
        rating: str | None = None,
        star: bool = False,
        enabled: bool = False,
    ) -> None:
        self.rating.selected = rating
        self.star.selected = "star" if star else None
        for button in self.evaluation.query(Button):
            button.disabled = not enabled

    def to_request(self) -> CompletionRequest:
        stop_words = list(filter(len, unescape(self.stop_words.value).split(" ")))
        return CompletionRequest(
            model=self.model.value,
            prompt=unescape(self.prompt.value),
            temperature=float(self.temperature.value),
            max_tokens=int(self.max_tokens.value),
            stop=(stop_words if len(stop_words) else None),
        )
