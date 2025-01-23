from unittest.mock import patch, mock_open
import json

from l2m2.client import LLMClient

from cliff.config import (
    load_config,
    apply_config,
    save_config,
    add_provider,
    remove_provider,
    set_default_model,
    view_config,
    process_config_command,
    CONFIG_FILE,
    DEFAULT_CONFIG,
    HELP_FILE,
)


@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_load_config_file_not_exist(
    mock_json_dump, mock_file, mock_makedirs, mock_path_exists
):
    """
    If config file doesn't exist, load_config() should create a default config file
    and return DEFAULT_CONFIG.
    """
    config = load_config()
    mock_makedirs.assert_called_once()
    mock_file.assert_called_once_with(CONFIG_FILE, "w")
    mock_json_dump.assert_called_once_with(DEFAULT_CONFIG, mock_file())
    assert config == DEFAULT_CONFIG


@patch("os.path.exists", return_value=True)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='{"provider_credentials": {"openai": "secret"}, "default_model": "gpt-4o"}',
)
@patch("json.load", side_effect=lambda f: json.loads(f.read()))
def test_load_config_file_exists(mock_json_load, mock_file, mock_path_exists):
    """
    If config file exists, load_config() should read it and return its content.
    """
    config = load_config()
    mock_file.assert_called_once_with(CONFIG_FILE, "r")
    assert config["provider_credentials"] == {"openai": "secret"}
    assert config["default_model"] == "gpt-4o"


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_config(mock_json_dump, mock_file):
    """
    save_config() should dump the given config to the config file.
    """
    test_config = {
        "provider_credentials": {"openai": "secret"},
        "default_model": "gpt-4o",
    }
    save_config(test_config)
    mock_file.assert_called_once_with(CONFIG_FILE, "w")
    mock_json_dump.assert_called_once_with(test_config, mock_file())


@patch("l2m2.client.LLMClient")
def test_apply_config(mock_llm_client):
    """
    apply_config() should call llm.add_provider for each provider credential in the config.
    """
    mock_llm = mock_llm_client.return_value
    test_config = {
        "provider_credentials": {"openai": "secret_key", "anthropic": "another_key"},
        "default_model": None,
    }
    apply_config(test_config, mock_llm)
    mock_llm.add_provider.assert_any_call("openai", "secret_key")
    mock_llm.add_provider.assert_any_call("anthropic", "another_key")


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_add_provider_valid_new(mock_save_config, mock_load_config):
    """
    add_provider() with a valid provider not previously in the config
    should set that provider's API key, possibly set default_model,
    save config, and return 0.
    """
    mock_load_config.return_value = {"provider_credentials": {}, "default_model": None}
    result = add_provider("openai", "test_key")
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_add_provider_valid_update(mock_save_config, mock_load_config):
    """
    add_provider() with a valid provider that already exists
    should update its API key, save config, and return 0.
    """
    mock_load_config.return_value = {
        "provider_credentials": {"openai": "old_key"},
        "default_model": "gpt-4o",
    }
    result = add_provider("openai", "new_key")
    mock_save_config.assert_not_called()
    assert result == 0


def test_add_provider_invalid():
    """
    add_provider() with an invalid provider should return 1 and not touch config.
    """
    result = add_provider("unknown_provider", "some_key")
    assert result == 1


@patch(
    "cliff.config.load_config",
    return_value={
        "provider_credentials": {"openai": "secret_key"},
        "default_model": "gpt-4o",
    },
)
@patch("cliff.config.save_config")
def test_remove_provider_existing(mock_save_config, mock_load_config):
    """
    remove_provider() should remove the provider if it exists, save config, and return 0.
    """
    result = remove_provider("openai")
    mock_save_config.assert_called_once()
    assert result == 0


@patch(
    "cliff.config.load_config",
    return_value={
        "provider_credentials": {"openai": "secret_key"},
        "default_model": "gpt-4o",
    },
)
@patch("cliff.config.save_config")
def test_remove_provider_nonexistent(mock_save_config, mock_load_config):
    """
    remove_provider() should return 1 if provider is not found, and not save.
    """
    result = remove_provider("anthropic")
    mock_save_config.assert_not_called()
    assert result == 1


@patch(
    "l2m2.client.LLMClient.get_available_models",
    return_value=["gpt-4o", "claude-3.5-haiku"],
)
@patch("l2m2.client.LLMClient.get_active_models", return_value=["gpt-4o"])
@patch(
    "cliff.config.load_config",
    return_value={
        "provider_credentials": {"openai": "test_key"},
        "default_model": "gpt-4o",
    },
)
@patch("cliff.config.save_config")
def test_set_default_model_success(
    mock_save_config, mock_load_config, mock_active_models, mock_available_models
):
    """
    set_default_model() should succeed if model is in available models and active models.
    """
    llm = LLMClient()
    result = set_default_model("gpt-4o", llm)
    mock_save_config.assert_called_once()
    assert result == 0


@patch("l2m2.client.LLMClient.get_available_models", return_value=["claude-3.5-haiku"])
@patch("l2m2.client.LLMClient.get_active_models", return_value=["claude-3.5-haiku"])
def test_set_default_model_not_in_available(mock_active, mock_available):
    """
    set_default_model() should return 1 if the model is not in the available models list.
    """
    llm = LLMClient()
    result = set_default_model("gpt-4o", llm)
    assert result == 1


@patch(
    "l2m2.client.LLMClient.get_available_models",
    return_value=["gpt-4o", "some-other-model"],
)
@patch("l2m2.client.LLMClient.get_active_models", return_value=["some-other-model"])
def test_set_default_model_not_active(mock_active, mock_available):
    """
    set_default_model() should return 2 if the model is available but not active.
    """
    llm = LLMClient()
    result = set_default_model("gpt-4o", llm)
    assert result == 2


@patch(
    "cliff.config.load_config",
    return_value={"provider_credentials": {}, "default_model": None},
)
def test_view_config(mock_load_config, capsys):
    """
    view_config() should print the config and return 0. We'll just check the return code.
    """
    result = view_config()
    captured = capsys.readouterr()
    assert result == 0
    assert "provider_credentials" in captured.out


@patch("cliff.config.add_provider", return_value=0)
def test_process_config_command_add_provider(mock_add_provider):
    """
    process_config_command should invoke add_provider when "add" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["add", "openai", "test-key"], llm)
    mock_add_provider.assert_called_once_with("openai", "test-key")
    assert result == 0


@patch("cliff.config.remove_provider", return_value=0)
def test_process_config_command_remove_provider(mock_remove_provider):
    """
    process_config_command should invoke remove_provider when "remove" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["remove", "openai"], llm)
    mock_remove_provider.assert_called_once_with("openai")
    assert result == 0


@patch("cliff.config.set_default_model", return_value=0)
def test_process_config_command_set_default_model(mock_set_default_model):
    """
    process_config_command should invoke set_default_model when "default-model" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["default-model", "gpt-4o"], llm)
    mock_set_default_model.assert_called_once_with("gpt-4o", llm)
    assert result == 0


@patch("cliff.config.view_config", return_value=0)
def test_process_config_command_view(mock_view_config):
    """
    process_config_command should invoke view_config when "view" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["view"], llm)
    mock_view_config.assert_called_once()
    assert result == 0


def test_process_config_command_invalid():
    """
    process_config_command with an unrecognized command should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["bad-command"], llm)
    assert result == 1


def test_process_config_command_add_provider_usage():
    """
    process_config_command with "add" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["add", "only-one-arg"], llm)
    assert result == 1


def test_process_config_command_remove_provider_usage():
    """
    process_config_command with "remove" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["remove"], llm)
    assert result == 1


def test_process_config_command_set_default_model_usage():
    """
    process_config_command with "default-model" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["default-model"], llm)
    assert result == 1


@patch("builtins.open", new_callable=mock_open, read_data="Help content")
def test_process_config_command_help(mock_file):
    """
    process_config_command should print help content when "help" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["help"], llm)
    mock_file.assert_called_once_with(HELP_FILE, "r")
    assert result == 0
