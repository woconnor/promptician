import json
import openai
import os
import secrets

from dataclasses import dataclass

from asgiref.sync import sync_to_async


@dataclass
class CompletionRequest:
    model: str
    prompt: str
    temperature: int
    max_tokens: int
    stop: list[str] | None


@dataclass
class CompletionResult:
    id: str
    completion: str
    raw_request: dict[str, any]
    raw_response: dict[str, any]


class Client:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key != None:
            openai.api_key = self.api_key

    # TODO: Switch to async API once released. This currently leaves a socket unclosed :(
    # https://github.com/openai/openai-python/issues/98
    async def complete(self, req: CompletionRequest):
        raw_request = {
            "model": req.model,
            "prompt": req.prompt,
            "temperature": req.temperature,
            "max_tokens": req.max_tokens,
            "stop": req.stop,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

        response = await sync_to_async(openai.Completion.create)(**raw_request)
        completion = response.choices[0].text

        # Convert to dict so that it can later be written as YAML.
        raw_response = json.loads(json.dumps(response))

        return CompletionResult(
            id=secrets.token_hex(4),
            completion=completion,
            raw_request=raw_request,
            raw_response=raw_response,
        )
