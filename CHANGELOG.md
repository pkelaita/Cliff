# Changelog

_Current version: 0.0.3_

[PyPi link](https://pypi.org/project/cliff-cli/)

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
