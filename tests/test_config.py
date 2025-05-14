import os
import json
from copy import deepcopy

import pytest
from unittest.mock import patch, mock_open, MagicMock

from cliff.config import (
    add_ollama_model,
    add_provider,
    apply_config,
    CONFIG_FILE,
    Config,
    DEFAULT_CONFIG,
    DEFAULT_MODEL_MAPPING,
    HELP_FILE,
    load_config,
    prefer_add,
    prefer_remove,
    process_config_command,
    remove_ollama_model,
    remove_provider,
    reset_config,
    save_config,
    set_default_model,
    show_config,
    update_memory_window,
    update_timeout,
    validate_model,
    validate_provider,
)


# -- Fixtures -- #


@pytest.fixture
def default_config_copy():
    """Return a fresh copy of the default configuration."""
    return deepcopy(DEFAULT_CONFIG)


@pytest.fixture
def dummy_llm():
    """Return a dummy LLMClient-like object with needed attributes."""
    dummy = MagicMock()
    # For validate_model, assume by default the active models include 'dummy-model'
    dummy.get_active_models.return_value = ["dummy-model"]
    return dummy


# -- Tests for File Operations -- #


def test_save_config(default_config_copy):
    """save_config should write the JSON configuration to CONFIG_FILE."""
    m = mock_open()
    with (
        patch("cliff.config.open", m, create=True),
        patch("json.dump") as mock_json_dump,
    ):
        save_config(default_config_copy)
        m.assert_called_once_with(CONFIG_FILE, "w")
        mock_json_dump.assert_called_once_with(
            default_config_copy.model_dump(), m(), indent=4
        )


def test_load_config_file_not_exist():
    """load_config should create directories and save the default config when file does not exist."""
    with (
        patch("cliff.config.os.path.exists", return_value=False),
        patch("cliff.config.os.makedirs") as mock_makedirs,
        patch("cliff.config.save_config") as mock_save,
    ):
        config = load_config()
        assert isinstance(config, Config)
        assert config == DEFAULT_CONFIG
        mock_makedirs.assert_called_once_with(
            os.path.dirname(CONFIG_FILE), exist_ok=True
        )
        mock_save.assert_called_once_with(DEFAULT_CONFIG)


def test_load_config_file_exists_missing_fields():
    """load_config should complete a config file that is missing some fields."""
    partial_config = {
        "provider_credentials": {"openai": "dummy-key"},
        "default_model": "dummy-model",
    }

    m_open = mock_open(read_data=json.dumps(partial_config))
    with (
        patch("cliff.config.os.path.exists", return_value=True),
        patch("cliff.config.open", m_open, create=True),
        patch("cliff.config.save_config") as mock_save,
    ):
        config = load_config()
        assert isinstance(config, Config)
        assert config.provider_credentials == {"openai": "dummy-key"}
        assert config.default_model == "dummy-model"
        mock_save.assert_called_once()


def test_load_config_file_exists_invalid_json():
    """load_config should handle invalid JSON in the config file."""
    m_open = mock_open(read_data="invalid json")
    with (
        patch("cliff.config.os.path.exists", return_value=True),
        patch("cliff.config.open", m_open, create=True),
        patch("cliff.config.save_config") as mock_save,
    ):
        config = load_config()
        assert isinstance(config, Config)
        assert config == DEFAULT_CONFIG
        mock_save.assert_called_once_with(DEFAULT_CONFIG)


# -- Tests for Apply Config -- #


def test_apply_config():
    """apply_config should update the llm with provider credentials, preferred providers and local models."""
    config = Config(
        provider_credentials={"openai": "abc123"},
        default_model="openai-model",
        preferred_providers={"dummy-model": "openai"},
        ollama_models=["local-model"],
        memory_window=10,
        timeout_seconds=20,
    )
    dummy_llm = MagicMock()
    with patch("cliff.config.load_config", return_value=config):
        apply_config(config, dummy_llm)
        # add_provider is called for each provider credential
        dummy_llm.add_provider.assert_called_once_with("openai", "abc123")
        dummy_llm.set_preferred_providers.assert_called_once_with(
            {"dummy-model": "openai"}
        )
        dummy_llm.add_local_model.assert_called_once_with("local-model", "ollama")


# -- Tests for Validators -- #


def test_validate_provider_valid():
    """validate_provider should return True for a valid provider."""
    # Choose any from the static set, e.g., "openai"
    assert validate_provider("openai") is True


def test_validate_provider_invalid():
    """validate_provider should return False and print error for an invalid provider."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = validate_provider("invalid-provider")
        assert result is False
        mock_print.assert_called_once_with("Invalid provider: invalid-provider")


def test_validate_model_valid(dummy_llm):
    """validate_model should return True if model is in llm.get_active_models()."""
    dummy_llm.get_active_models.return_value = ["dummy-model", "other-model"]
    assert validate_model("dummy-model", dummy_llm) is True


def test_validate_model_invalid(dummy_llm):
    """validate_model should return False and print error if model is not found."""
    dummy_llm.get_active_models.return_value = ["other-model"]
    with patch("cliff.config.cliff_print") as mock_print:
        result = validate_model("dummy-model", dummy_llm)
        assert result is False
        mock_print.assert_called_once_with("Model dummy-model not found")


# -- Tests for Add/Update Functions -- #


def test_add_provider_invalid():
    """add_provider should return 1 if an invalid provider is given."""
    with (
        patch("cliff.config.validate_provider", return_value=False) as mock_validate,
        patch("cliff.config.cliff_print"),
    ):
        result = add_provider("invalid-provider", "key")
        assert result == 1
        mock_validate.assert_called_once_with("invalid-provider")


def test_add_provider_new():
    """add_provider should add a new valid provider and set default_model if None."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.validate_provider", return_value=True),
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = add_provider("openai", "new-key")
        assert result == 0
        assert dummy_config.provider_credentials["openai"] == "new-key"
        assert dummy_config.default_model == DEFAULT_MODEL_MAPPING["openai"]
        mock_print.assert_called_once_with("Added provider openai")


def test_add_provider_update():
    """add_provider should update an existing valid provider."""
    dummy_config = Config(
        provider_credentials={"openai": "old-key"},
        default_model="existing-model",
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.validate_provider", return_value=True),
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = add_provider("openai", "updated-key")
        assert result == 0
        assert dummy_config.provider_credentials["openai"] == "updated-key"
        assert dummy_config.default_model == "existing-model"
        mock_print.assert_called_once_with("Updated provider openai")


def test_add_ollama_model():
    """add_ollama_model should append the model and set default_model if None."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = add_ollama_model("local-model")
        assert result == 0
        assert "local-model" in dummy_config.ollama_models
        assert dummy_config.default_model == "local-model"
        mock_print.assert_called_once_with("Added local model local-model")


def test_set_default_model_invalid(dummy_llm):
    """set_default_model should return 1 if the model is invalid."""
    with (
        patch("cliff.config.validate_model", return_value=False) as mock_validate,
        patch("cliff.config.cliff_print"),
    ):
        result = set_default_model("non-existent", dummy_llm)
        assert result == 1
        mock_validate.assert_called_once_with("non-existent", dummy_llm)


def test_set_default_model_valid(dummy_llm):
    """set_default_model should update default_model when the model is valid."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.validate_model", return_value=True),
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = set_default_model("dummy-model", dummy_llm)
        assert result == 0
        assert dummy_config.default_model == "dummy-model"
        mock_print.assert_called_once_with("Set default model to dummy-model")


def test_prefer_add_invalid_model(dummy_llm):
    """prefer_add should return 1 if the model is invalid."""
    with (
        patch("cliff.config.validate_model", return_value=False) as mock_val_model,
        patch("cliff.config.cliff_print"),
    ):
        result = prefer_add("non-existent", "openai", dummy_llm)
        assert result == 1
        mock_val_model.assert_called_once_with("non-existent", dummy_llm)


def test_prefer_add_invalid_provider(dummy_llm):
    """prefer_add should return 1 if the provider is invalid."""
    with (
        patch("cliff.config.validate_model", return_value=True),
        patch(
            "cliff.config.validate_provider", return_value=False
        ) as mock_val_provider,
        patch("cliff.config.cliff_print"),
    ):
        result = prefer_add("dummy-model", "invalid-provider", dummy_llm)
        assert result == 1
        mock_val_provider.assert_called_once_with("invalid-provider")


def test_prefer_add_valid(dummy_llm):
    """prefer_add should update the preferred_providers for a valid model and provider."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.validate_model", return_value=True),
        patch("cliff.config.validate_provider", return_value=True),
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = prefer_add("dummy-model", "openai", dummy_llm)
        assert result == 0
        assert dummy_config.preferred_providers["dummy-model"] == "openai"
        mock_print.assert_called_once_with(
            "Added preferred provider openai for dummy-model"
        )


def test_update_memory_window_invalid():
    """update_memory_window should return 1 if invalid window provided."""
    with patch("cliff.config.cliff_print"):
        assert update_memory_window("-1") == 1
        assert update_memory_window("abc") == 1


def test_update_memory_window_valid():
    """update_memory_window should update memory_window in config if valid."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = update_memory_window("15")
        assert result == 0
        assert dummy_config.memory_window == 15
        mock_print.assert_called_once_with("Updated memory window size to 15")


def test_update_timeout_invalid():
    """update_timeout should return 1 if timeout is invalid."""
    with (patch("cliff.config.cliff_print"),):
        assert update_timeout("0") == 1
        assert update_timeout("-1") == 1
        assert update_timeout("abc") == 1


def test_update_timeout_valid():
    """update_timeout should update timeout_seconds in config if valid."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = update_timeout("25")
        assert result == 0
        assert dummy_config.timeout_seconds == 25
        mock_print.assert_called_once_with("Updated timeout to 25 seconds")


# -- Tests for Remove Functions -- #


def test_remove_provider_not_found():
    """remove_provider should return 1 if provider is not in config."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    # No provider credentials set initially.
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = remove_provider("openai")
        assert result == 1
        mock_print.assert_called_once_with("Provider openai not found")


def test_remove_provider_found():
    """remove_provider should remove an existing provider."""
    dummy_config = Config(
        provider_credentials={"openai": "key123"},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = remove_provider("openai")
        assert result == 0
        assert "openai" not in dummy_config.provider_credentials
        mock_print.assert_called_once_with("Removed provider openai")


def test_remove_ollama_model_not_found():
    """remove_ollama_model should return 1 if the model is not present."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = remove_ollama_model("nonexistent")
        assert result == 1
        mock_print.assert_called_once_with("local model nonexistent not found")


def test_remove_ollama_model_found():
    """remove_ollama_model should remove the model if present."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=["local-model"],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = remove_ollama_model("local-model")
        assert result == 0
        assert "local-model" not in dummy_config.ollama_models
        mock_print.assert_called_once_with("Removed local model local-model")


def test_prefer_remove_not_found():
    """prefer_remove should return 1 if preferred provider for model does not exist."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = prefer_remove("dummy-model")
        assert result == 1
        mock_print.assert_called_once_with(
            "Preferred provider for dummy-model not found"
        )


def test_prefer_remove_found():
    """prefer_remove should remove the preferred provider entry if present."""
    dummy_config = Config(
        provider_credentials={},
        default_model=None,
        preferred_providers={"dummy-model": "openai"},
        ollama_models=[],
        memory_window=10,
        timeout_seconds=20,
    )
    with (
        patch("cliff.config.load_config", return_value=dummy_config),
        patch("cliff.config.save_config"),
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = prefer_remove("dummy-model")
        assert result == 0
        assert "dummy-model" not in dummy_config.preferred_providers
        mock_print.assert_called_once_with("Removed preferred provider for dummy-model")


# -- Tests for Misc Functions -- #


def test_reset_config():
    """reset_config should call save_config with DEFAULT_CONFIG and print a reset message."""
    with (
        patch("cliff.config.save_config") as mock_save,
        patch("cliff.config.cliff_print") as mock_print,
    ):
        result = reset_config()
        assert result == 0
        mock_save.assert_called_once_with(DEFAULT_CONFIG)
        mock_print.assert_called_once_with("Reset config to defaults")


def test_show_config():
    """show_config should print the config table and help message, and return 0."""
    full_config = Config(
        provider_credentials={"openai": "abc123", "google": "xyz789"},
        default_model="gpt-4o",
        preferred_providers={"dummy-model": "openai", "other-model": "google"},
        ollama_models=["local-model-1", "local-model-2"],
        memory_window=15,
        timeout_seconds=30,
    )

    with (
        patch("cliff.config.load_config", return_value=full_config),
        patch("cliff.config.console") as mock_console,
        patch("builtins.print") as mock_builtin_print,
    ):
        result = show_config()
        assert result == 0
        assert mock_console.print.call_count >= 1
        assert mock_builtin_print.call_count >= 2


def test_show_config_default():
    """show_config should print the config table and help message, and return 0."""
    with (
        patch("cliff.config.load_config", return_value=DEFAULT_CONFIG),
        patch("cliff.config.console") as mock_console,
        patch("builtins.print") as mock_builtin_print,
    ):
        result = show_config()
        assert result == 0
        assert mock_console.print.call_count >= 1
        assert mock_builtin_print.call_count >= 2


# -- Tests for process_config_command function -- #


def test_help_command_empty(dummy_llm):
    """process_config_command with empty or 'help' should call resource_print and return 0."""
    with patch("cliff.config.resource_print") as mock_resource_print:
        result = process_config_command([], dummy_llm)
        assert result == 0
        mock_resource_print.assert_called_once_with(HELP_FILE)
    with patch("cliff.config.resource_print") as mock_resource_print:
        result = process_config_command(["help"], dummy_llm)
        assert result == 0
        mock_resource_print.assert_called_once_with(HELP_FILE)


def test_add_wrong_usage(dummy_llm):
    """process_config_command 'add' with wrong parameters should print usage and return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["add", "openai"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with(
            "Usage: add [provider] [api-key] or add ollama [model]"
        )


def test_add_ollama(dummy_llm):
    """process_config_command 'add ollama [model]' should call add_ollama_model."""
    with patch("cliff.config.add_ollama_model", return_value=0) as mock_add:
        result = process_config_command(["add", "ollama", "local-model"], dummy_llm)
        assert result == 0
        mock_add.assert_called_once_with("local-model")


def test_add_provider(dummy_llm):
    """process_config_command 'add [provider] [key]' should call add_provider."""
    with patch("cliff.config.add_provider", return_value=0) as mock_add:
        result = process_config_command(["add", "openai", "apikey"], dummy_llm)
        assert result == 0
        mock_add.assert_called_once_with("openai", "apikey")


def test_remove_wrong_usage(dummy_llm):
    """process_config_command 'remove' with insufficient args should print usage and return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["remove"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with(
            "Usage: remove [provider] or remove ollama [model]"
        )


def test_remove_ollama_wrong_usage(dummy_llm):
    """process_config_command 'remove ollama' with insufficient args returns 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["remove", "ollama"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with("Usage: remove ollama [model]")


def test_remove_ollama(dummy_llm):
    """process_config_command 'remove ollama [model]' should call remove_ollama_model."""
    with patch("cliff.config.remove_ollama_model", return_value=0) as mock_remove:
        result = process_config_command(["remove", "ollama", "local-model"], dummy_llm)
        assert result == 0
        mock_remove.assert_called_once_with("local-model")


def test_remove_provider(dummy_llm):
    """process_config_command 'remove [provider]' should call remove_provider."""
    with patch("cliff.config.remove_provider", return_value=0) as mock_remove:
        result = process_config_command(["remove", "openai"], dummy_llm)
        assert result == 0
        mock_remove.assert_called_once_with("openai")


def test_default_model_wrong_usage(dummy_llm):
    """process_config_command 'default-model' with wrong usage returns 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["default-model"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with("Usage: default-model [model]")


def test_default_model(dummy_llm):
    """process_config_command 'default-model [model]' should call set_default_model."""
    with patch("cliff.config.set_default_model", return_value=0) as mock_set:
        result = process_config_command(["default-model", "dummy-model"], dummy_llm)
        assert result == 0
        mock_set.assert_called_once_with("dummy-model", dummy_llm)


def test_prefer_wrong_usage(dummy_llm):
    """process_config_command 'prefer' with wrong parameters should return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["prefer"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with(
            "Usage: prefer [model] [provider] or prefer remove [model]"
        )


def test_prefer_remove(dummy_llm):
    """process_config_command 'prefer remove [model]' should call prefer_remove."""
    with patch("cliff.config.prefer_remove", return_value=0) as mock_remove:
        result = process_config_command(["prefer", "remove", "dummy-model"], dummy_llm)
        assert result == 0
        mock_remove.assert_called_once_with("dummy-model")


def test_prefer_add(dummy_llm):
    """process_config_command 'prefer [model] [provider]' should call prefer_add."""
    with patch("cliff.config.prefer_add", return_value=0) as mock_add:
        result = process_config_command(["prefer", "dummy-model", "openai"], dummy_llm)
        assert result == 0
        mock_add.assert_called_once_with("dummy-model", "openai", dummy_llm)


def test_memory_window_wrong_usage(dummy_llm):
    """process_config_command 'memory-window' with wrong usage should print usage and return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["memory-window"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with("Usage: memory-window [window-size]")


def test_memory_window(dummy_llm):
    """process_config_command 'memory-window [size]' should call update_memory_window."""
    with patch("cliff.config.update_memory_window", return_value=0) as mock_update:
        result = process_config_command(["memory-window", "20"], dummy_llm)
        assert result == 0
        mock_update.assert_called_once_with("20")


def test_timeout_wrong_usage(dummy_llm):
    """process_config_command 'timeout' with wrong usage should print usage and return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["timeout"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with("Usage: timeout [seconds]")


def test_timeout(dummy_llm):
    """process_config_command 'timeout [seconds]' should call update_timeout."""
    with patch("cliff.config.update_timeout", return_value=0) as mock_update:
        result = process_config_command(["timeout", "30"], dummy_llm)
        assert result == 0
        mock_update.assert_called_once_with("30")


def test_reset(dummy_llm):
    """process_config_command 'reset' should call reset_config."""
    with patch("cliff.config.reset_config", return_value=0) as mock_reset:
        result = process_config_command(["reset"], dummy_llm)
        assert result == 0
        mock_reset.assert_called_once()


def test_show(dummy_llm):
    """process_config_command 'show' should call show_config."""
    with patch("cliff.config.show_config", return_value=0) as mock_show:
        result = process_config_command(["show"], dummy_llm)
        assert result == 0
        mock_show.assert_called_once()


def test_unrecognized_command(dummy_llm):
    """process_config_command with unknown command should print error and return 1."""
    with patch("cliff.config.cliff_print") as mock_print:
        result = process_config_command(["notacommand"], dummy_llm)
        assert result == 1
        mock_print.assert_called_once_with(
            "Unrecognized config command: notacommand. For usage, run cliff --config help"
        )
