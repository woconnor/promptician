import os
from dataclasses import dataclass, asdict
from pathlib import Path
from ruamel.yaml import YAML


def get_path() -> Path:
    config = os.getenv("PROMPTICIAN_PATH")
    return Path(config) if config else Path.home() / "promptician.yaml"


@dataclass
class PromptCompletion:
    """A completed prompt with optional evaluation"""

    id: str
    prompt: str
    completion: str
    rating: str | None
    star: bool | None
    raw_request: dict[str, any]
    raw_response: dict[str, any]


class Repository:
    """A prompt completion store persisted as YAML."""

    def __init__(self) -> None:
        self.yaml = YAML(typ="safe")
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.default_flow_style = False
        self.path = get_path()
        self._load()

    def items(self) -> list[PromptCompletion]:
        return self._items.values()

    def upsert(self, item: PromptCompletion) -> None:
        # Update existing item or insert new item at beginning.
        if item.id in self._items:
            self._items[item.id] = item
        else:
            items = {item.id: item}
            items.update(self._items)
            self._items = items
        self._save()

    def _load(self) -> None:
        try:
            self._items = {}
            docs = list(self.yaml.load_all(self.path))
            for doc in docs:
                if doc != None:
                    self._items[doc["id"]] = PromptCompletion(**doc)
        except Exception as err:
            print(err)

    def _save(self) -> None:
        try:
            docs = []
            for item in self._items.values():
                docs.append(asdict(item))
            self.yaml.dump_all(docs, self.path)
        except Exception as err:
            print(err)
