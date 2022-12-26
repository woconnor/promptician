# Promptician

A text user interface for composing GPT-3 prompts and evaluating completions.
Written in Python using the Textual framework.


## Setup

An OpenAI API key is needed to make requests to GPT-3. The app expects to find
the key in the `OPENAI_API_KEY` environment variable. Sign up for a free account
at <https://openai.com/>

Prompt completions are saved as YAML to `PROMPTICIAN_PATH`, which defaults to
`promptician.yaml` in the home directory.


## Run

Install dependencies and run with Poetry:

``` sh
poetry install
poetry run python -m promptician_app
```

For development, it is useful to run with the Textual console:

``` sh
# terminal 1
textual console

# terminal 2
textual run --dev promptician_app:PrompticianApp
```
