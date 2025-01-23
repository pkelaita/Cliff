# Cliff

Cliff (**C**ommand **L**ine **I**nter**F**ace **F**riend) is an AI assistant that helps you come up with Unix commands. Given an objective (for example, "kill the process running on port 8080"), Cliff will generate a command that does the objective and add it to your clipboard for you to easily paste into your terminal.

## Why?

It's annoying having to open the browser when I forget how to do something in the terminal.

## Requirements

- Python >= 3.9
- A valid API key from [OpenAI](https://platform.openai.com/), [Anthropic](https://www.anthropic.com/api), [Google](https://ai.google.dev/), [Cohere](https://cohere.com/), [Groq](https://console.groq.com/login), [Replicate](https://replicate.com/), [Mistral](https://docs.mistral.ai/deployment/laplateforme/overview/), or [Cerebras](https://cloud.cerebras.ai/).
- A Unix-like operating system

## Installation

You can install Cliff with homebrew:

```bash
brew tap pkelaita/cliff
brew install cliff
```

Or with pip:

```bash
pip install cliff-cli
```

## Configuration

Add your LLM provider API credentials as follows:

```
cliff --config add [provider] [api key]
```

The provider can be any of `openai`, `anthropic`, `google`, `cohere`, `groq`, `replicate`, `mistral`, or `cerebras`.

For a full overview of the configuration system, run `cliff --config help`, and for a full list of supported models for each provider, see [L2M2's docs](https://github.com/pkelaita/l2m2/blob/main/docs/supported_models.md).

## Usage

Get started by running `cliff` with an objective.

```
cliff kill the process running on port 8080
```

Cliff will automatically add the command to your paste buffer, so no need to copy-paste it.

If needed (i.e., to avoid escaping special characters), you can use quotes.

```bash
cliff "kill the process that's running on port 8080"
```

If you want to specify which model to use, you can do so with the `--model` flag.

```
cliff --model gpt-4o-mini kill the process running on port 8080
```

You can set the default model with `cliff --config default-model [model]`.

**Recalling Command Outputs:**

Optionally, you can share commands you've ran and their outputs with Cliff to help it debug and improve its responses.

- To run a command and store its output for Cliff, run `cliff -r <command>` or `cliff --recall <command>`.
- To view all recalled commands and their outputs, run `cliff --view-recall` or `cliff -vr`.
- To clear Cliff's recall storage, run `cliff --clear-recall` or `cliff -cr`.

To view the man page, run `cliff` with no arguments.

That's it! It's pretty simple which is the point.

## Planned Features

- Chat mode with sliding memory
- Support for Ollama (I need to update [L2M2](https://github.com/pkelaita/l2m2) for this)
- Other features as they come to mind
