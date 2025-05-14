# Changelog

_Current version: 0.5.1_

[PyPi link](https://pypi.org/project/cliff-cli/)

### 0.5.2 - May 14, 2025

#### Changed

- Updated [L2M2](https://github.com/pkelaita/l2m2) from v0.0.51 to v0.0.53, which adds Gemini 2.5 Flash and upates Gemini 2.5 Pro to the latest API version.
- Improved DevX by adding [ty](https://github.com/astral-sh/ty) for type checking and Pydantic for config validation.

### 0.5.1 - May 1, 2025

#### Changed

- Updated [L2M2](https://github.com/pkelaita/l2m2) from v0.0.49 to v0.0.51, which adds a ton of new models, including o3, GPT-4.1, Llama 4, and more. See the L2M2 [release notes](https://github.com/pkelaita/l2m2/releases/tag/v0.0.51) for all of the new models added, and see Cliff's [supported models](https://github.com/pkelaita/cliff/blob/main/docs/supported_models.md) page for the latest list of supported models.
- Updated some of the default models for providers:
  - OpenAI: `gpt-4o` → `gpt-4.1`
  - Mistral: `mistral-small` → `codestral`
  - Anthropic: `claude-3.5-sonnet` → `claude-3.7-sonnet`

### 0.5.0 - March 27, 2025

#### Added

- Upgraded [L2M2](https://github.com/pkelaita/l2m2) from v0.0.46 to v0.0.49, which adds support for Google's [Gemini-2.5-Pro](https://blog.google/technology/google-deepmind/gemini-model-thinking-updates-march-2025/), Mistral's [Mistral-Saba](https://mistral.ai/news/mistral-saba) (via both Mistral Cloud and Groq), OpenAI's [o1-pro](https://platform.openai.com/docs/models/o1-pro), and Cohere's [Command-A](https://cohere.com/blog/command-a).

#### Changed

- Updated the default model for Cohere from `command-r` to `command-a`.

### 0.4.0 - March 12, 2025

#### Added

- Upgraded [L2M2](https://github.com/pkelaita/l2m2) from v0.0.44 to v0.0.46, which adds support for [GPT-4.5](https://openai.com/index/introducing-gpt-4-5/).

#### Fixed

- L2M2's [v0.0.45](https://github.com/pkelaita/l2m2/releases/tag/v0.0.45) and [v0.0.46](https://github.com/pkelaita/l2m2/releases/tag/v0.0.46) updates also both patch a few small bugs with reasoning models.

### 0.3.0 - February 24, 2025

#### Added

- Updated [L2M2](https://github.com/pkelaita/l2m2) from v0.0.43 to v0.0.44, which adds support for Anthropic's [Claude 3.7 Sonnet](https://www.anthropic.com/news/claude-3-7-sonnet) model released today.

### 0.2.2 - February 24, 2025

#### Fixed

- Fixed an issue where passing in invalid config values (such as `cliff --config memory-window -1`) would make the configuration system unusable by adding validation checks to the config system.

### 0.2.1 - February 22, 2025

#### Fixed

- Fixed an issue where man pages were being improperly indented.

### 0.2.0 - February 22, 2025

#### Added

- [L2M2](https://github.com/pkelaita/l2m2) has been updated from v0.0.41 to v0.0.43, which adds support for the following models:
  - `o3-mini` via OpenAI
  - `gemini-2.0-pro` and `gemini-2.0-flash-lite` via Google
  - `qwen-2.5-32b`, `deepseek-r1-distill-qwen-32b`, and `deepseek-r1-distill-llama-70b` via Groq
  - `command-r7b` via Cohere
- Malformed or out-of-date config files are now automatically corrected and/or handled gracefully.
- Added a new command, `cliff --clear`, which is a shortcut for `cliff --memory clear && cliff --notepad clear`.
- Added GitHub Actions for CI/CD.

#### Changed

- Standard outputs, such as `cliff --config show` and `cliff --memory show`, are now formatted and colorized with [Rich](https://github.com/Textualize/rich).
- Some default models have been switched back to their larger counterparts due to improved quality and latency.
  - OpenAI: `gpt-4o-mini` → `gpt-4o`
  - Groq: `llama-3.2-1b` → `llama-3.3-70b`
  - Replicate: `llama-3-8b` → `llama-3-70b`
  - Cerebras: `llama-3.1-8b` → `llama-3.3-70b`
  - Anthropic: `claude-3.5-haiku` → `claude-3.5-sonnet`
  - Cohere: `command-r7b` → `command-r`
- Man pages now print in pager mode.

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
