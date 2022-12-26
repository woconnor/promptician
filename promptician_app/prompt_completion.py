from dataclasses import dataclass, asdict


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

    def to_dict(self) -> dict[str, any]:
        return asdict(self)
