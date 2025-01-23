from typing import Dict, Optional, List
import os
import json

from l2m2.client import LLMClient

DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(DIR, "resources/cliff.config.json")
HELP_FILE = os.path.join(DIR, "resources/config_help.txt")

VALID_PROVIDERS = {
    "groq",
    "cohere",
    "mistral",
    "replicate",
    "openai",
    "cerebras",
    "google",
    "anthropic",
}

DEFAULT_MODEL_MAPPING = {
    "groq": "llama-3.2-1b",
    "cohere": "command-r-plus",
    "mistral": "mistral-small",
    "replicate": "llama-3-8b",
    "openai": "gpt-4o",
    "cerebras": "gemma2-9b",
    "google": "gemini-2.0-flash",
    "anthropic": "claude-3.5-haiku",
}

Config = Dict[str, Optional[Dict[str, str]]]

DEFAULT_CONFIG: Config = {
    "provider_credentials": {},
    "default_model": None,
}


def load_config() -> Config:
    if not os.path.exists(CONFIG_FILE):
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f)
        config = DEFAULT_CONFIG
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

    return config


def apply_config(config: Config, llm: LLMClient) -> None:
    for provider in config["provider_credentials"]:  # type: ignore
        llm.add_provider(provider, config["provider_credentials"][provider])  # type: ignore


def save_config(config: Config) -> None:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def add_provider(provider: str, api_key: str) -> int:
    if provider not in VALID_PROVIDERS:
        print(f"[Cliff] Invalid provider: {provider}")
        return 1

    config = load_config()
    exists = config["provider_credentials"].get(provider)  # type: ignore

    config["provider_credentials"][provider] = api_key  # type: ignore

    if config["default_model"] is None:
        config["default_model"] = DEFAULT_MODEL_MAPPING[provider]  # type: ignore
        save_config(config)

    if exists:
        print(f"[Cliff] Updated provider {provider}")
        return 0
    else:
        print(f"[Cliff] Added provider {provider}")
        return 0


def remove_provider(provider: str) -> int:
    # TODO get the provider mapping from l2m2 to make sure we reset the default model if its provider is removed

    config = load_config()
    exists = config["provider_credentials"].get(provider)  # type: ignore

    if not exists:
        print(f"[Cliff] Provider {provider} not found")
        return 1

    del config["provider_credentials"][provider]  # type: ignore
    save_config(config)

    print(f"[Cliff] Removed provider {provider}")
    return 0


def set_default_model(model: str, llm: LLMClient) -> int:
    available_models = LLMClient.get_available_models()
    if model not in available_models:
        print(f"[Cliff] Model {model} not found")
        return 1

    active_models = llm.get_active_models()
    if model not in active_models:
        print(
            f"[Cliff] Model {model} available but not active. Please add its provider first."
        )
        return 2

    config = load_config()
    config["default_model"] = model  # type: ignore
    save_config(config)

    print(f"[Cliff] Set default model to {model}")
    return 0


def view_config() -> int:
    config = load_config()
    print(json.dumps(config, indent=4))
    return 0


def process_config_command(command: List[str], llm: LLMClient) -> int:
    if len(command) == 0 or command[0] == "help":
        with open(HELP_FILE, "r") as f:
            print(f.read())
        return 0

    elif command[0] == "add":
        if len(command) != 3:
            print("[Cliff] Usage: add [provider] [api-key]")
            return 1
        return add_provider(command[1], command[2])

    elif command[0] == "remove":
        if len(command) != 2:
            print("[Cliff] Usage: remove [provider]")
            return 1
        return remove_provider(command[1])

    elif command[0] == "default-model":
        if len(command) != 2:
            print("[Cliff] Usage: default-model [model]")
            return 1
        return set_default_model(command[1], llm)

    elif command[0] == "view":
        return view_config()

    else:
        print(
            f"[Cliff] expected either add, remove, default-model, view, or help, got {command[0]}"
        )
        return 1
