# Cliff

Cliff (**C**ommand **L**ine **I**nter**F**ace **F**riend) is an AI assistant that helps you come up with Unix commands. Given an objective (for example, "kill the process running on port 8080"), Cliff will generate a command that does the objective and add it to your clipboard for you to easily paste into your terminal.

## Why?

It's annoying having to open the browser when I forget how to do something in the terminal.

## Requirements

- Python >= 3.13
- A valid OpenAI API key
- A Unix-like operating system

## Installation

- Clone this repository
- In this repository, run `chmod +x run.sh`
- Create the file `~/envs/llm` and add your OpenAI API key to it in the format `OPENAI_API_KEY=sk-...`
- Add the following alias to your `.bashrc` or `.zshrc` (and source it):

```bash
alias cliff="path/to/cliff/run.sh"
```

- Run `cliff --install` to install the dependencies

## Usage

Get started by running `cliff` with an objective.

**Example:**

```bash
cliff kill the process running on port 8080
```

If needed (i.e., to avoid escaping special characters), you can use quotes.

```bash
cliff "kill the process that's running on port 8080"
```

Currently, cliff uses `gpt-4o` to generate commands.

**Recalling Command Outputs:**

Optionally, you can share commands you've ran and their outputs with Cliff to help it debug and improve its responses.

- To run a command and store its output for Cliff, run `cliff -r <command>` or `cliff --recall <command>`.
- To view all recalled commands and their outputs, run `cliff --view-recall` or `cliff -vr`.
- To clear Cliff's recall storage, run `cliff --clear-recall` or `cliff -cr`.

To view the man page, run `cliff` with no arguments.

That's it! It's pretty simple which is the point.

## Planned Features

- Install with homebrew
- Customize Cliff (e.g., which model to use) via a config file
- Chat mode with sliding memory
- Other features as they come to mind
