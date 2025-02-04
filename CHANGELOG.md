# Changelog

_Current version: 0.1.1_

[PyPi link](https://pypi.org/project/cliff-cli/)

### 0.1.1 - February 4, 2025

#### Fixed

- A bug where `cliff --memory show` would not truncate to the window size.
- A typo in one of the usage messages ("isage" instead of "usage").
- A bug where command outputs stored via `cliff --recall` would sometimes not be properly captured.

#### Improved

- The error message for a bad LLM response is now more consistent.
- A simple loading animation is now shown when the LLM is generating a response.

### 0.1.0 - February 3, 2025

#### Added

- Compatibility with local LLMs via [Ollama](https://ollama.ai/).
- Chat memory with a configurable sliding window.
- Preferred provider management via the config system in order to avoid model name conflicts between providers.
- Comprehensive unit tests.

#### Changed

- `cliff --config view`, `cliff --view-recall`, and `cliff -vr` have been renamed to `cliff --config show`, `cliff --show-recall`, and `cliff -sr` respectively for consistency.
- The output of `ls -al` is no longer included in the default system prompt.
- Updated default providers to use smaller models:
  - OpenAI: `gpt-4o` → `gpt-4o-mini`
  - Cohere: `command-r-plus` → `command-r`

#### Fixed

- In 0.0.3, the config file would only update on the first run. This has been fixed so it will always update as expected.
- Updated the default model for Cerebras from `gemma2-9b` (which is not a valid model ID) to `llama-3.1-8b`.

### 0.0.3 - January 22, 2025

#### Fixed

- In 0.0.2, there was an issue where configurations were sometimes not able to be changed when Cliff had been updated or multiple installations were present. This has been fixed by storing Cliff config files (config, recall) in `~/.cliff` instead of in the resources folder packaged with the application.

### 0.0.2 - January 21, 2025

#### Added

- Ability to configure Cliff with `cliff --config`

#### Removed

- No need to use `~/envs/llm` to store credentials anymore.

### 0.0.1 - January 20, 2025

The initial release. Basic functionality — generation with gpt-4o and recall ability.
