from unittest.mock import patch, mock_open, call

from l2m2.client import LLMClient

from cliff.config import (
    load_config,
    apply_config,
    save_config,
    add_provider,
    remove_provider,
    set_default_model,
    show_config,
    process_config_command,
    CONFIG_FILE,
    DEFAULT_CONFIG,
    HELP_FILE,
    prefer_add,
    prefer_remove,
    add_ollama,
    remove_ollama,
    update_memory_window,
    reset_config,
    update_timeout,
)


def get_test_base_config():
    """Returns a fresh copy of the base test configuration"""
    return {
        "provider_credentials": {},
        "default_model": None,
        "preferred_providers": {},
        "ollama_models": [],
        "memory_window": 10,
        "timeout_seconds": 20,
    }


def get_test_config_with_openai():
    """Returns a fresh copy of the OpenAI test configuration"""
    return {
        **get_test_base_config(),
        "provider_credentials": {"openai": "secret"},
        "default_model": "gpt-4o",
    }


def get_test_config_with_multiple_providers():
    """Returns a fresh copy of the multi-provider test configuration"""
    return {
        **get_test_base_config(),
        "provider_credentials": {"openai": "secret_key", "anthropic": "another_key"},
        "preferred_providers": {"gpt-4o": "openai"},
        "ollama_models": ["llama2", "mistral"],
    }


# -- Tests for Config File Operations -- #


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
    mock_json_dump.assert_called_once_with(DEFAULT_CONFIG, mock_file(), indent=4)
    assert config == DEFAULT_CONFIG


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open)
@patch("json.load")
def test_load_config_with_missing_fields(mock_json_load, mock_file, mock_path_exists):
    """
    Test that load_config() properly adds missing fields from DEFAULT_CONFIG when loading a partial config.
    """
    # Create a partial config missing some fields
    partial_config = {
        "provider_credentials": {"openai": "secret"},
        "default_model": "gpt-4o",
    }

    mock_json_load.return_value = partial_config

    config = load_config()

    # Check that missing fields were added with default values
    assert config["preferred_providers"] == DEFAULT_CONFIG["preferred_providers"]
    assert config["ollama_models"] == DEFAULT_CONFIG["ollama_models"]
    assert config["memory_window"] == DEFAULT_CONFIG["memory_window"]
    assert config["timeout_seconds"] == DEFAULT_CONFIG["timeout_seconds"]

    # Check that existing fields were preserved
    assert config["provider_credentials"] == {"openai": "secret"}
    assert config["default_model"] == "gpt-4o"


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_save_config(mock_json_dump, mock_file):
    """
    save_config() should dump the given config to the config file.
    """
    test_config = get_test_config_with_openai()
    save_config(test_config)
    mock_file.assert_called_once_with(CONFIG_FILE, "w")
    mock_json_dump.assert_called_once_with(test_config, mock_file(), indent=4)


# -- Tests for Provider Management -- #


@patch("l2m2.client.LLMClient")
def test_apply_config(mock_llm_client):
    """
    apply_config() should call llm.add_provider for each provider credential in the config.
    """
    mock_llm = mock_llm_client.return_value
    test_config = get_test_config_with_multiple_providers()
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
    mock_load_config.return_value = get_test_base_config()
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
    mock_load_config.return_value = get_test_config_with_openai()
    result = add_provider("openai", "new_key")
    mock_save_config.assert_called_once()
    assert result == 0


def test_add_provider_invalid():
    """
    add_provider() with an invalid provider should return 1 and not touch config.
    """
    result = add_provider("unknown_provider", "some_key")
    assert result == 1


@patch(
    "cliff.config.load_config",
    return_value=get_test_config_with_openai(),
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
    return_value=get_test_config_with_openai(),
)
@patch("cliff.config.save_config")
def test_remove_provider_nonexistent(mock_save_config, mock_load_config):
    """
    remove_provider() should return 1 if provider is not found, and not save.
    """
    result = remove_provider("anthropic")
    mock_save_config.assert_not_called()
    assert result == 1


# -- Tests for Default Model Management -- #


@patch(
    "l2m2.client.LLMClient.get_available_models",
    return_value=["gpt-4o", "claude-3.5-haiku"],
)
@patch("l2m2.client.LLMClient.get_active_models", return_value=["gpt-4o"])
@patch(
    "cliff.config.load_config",
    return_value=get_test_config_with_openai(),
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
    assert result == 1


# -- Tests for Preferred Provider Management -- #


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_prefer_add_success(mock_save_config, mock_load_config):
    """
    prefer_add() should add a preferred provider for a model and return 0.
    """
    mock_load_config.return_value = get_test_config_with_openai()
    result = prefer_add("gpt-4o", "openai")
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_prefer_remove_success(mock_save_config, mock_load_config):
    """
    prefer_remove() should remove a preferred provider for a model and return 0.
    """
    config = get_test_config_with_multiple_providers()
    mock_load_config.return_value = config
    result = prefer_remove("gpt-4o")
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_prefer_remove_nonexistent(mock_save_config, mock_load_config):
    """
    prefer_remove() should return 1 if the model has no preferred provider.
    """
    mock_load_config.return_value = get_test_config_with_openai()
    result = prefer_remove("gpt-4o")
    mock_save_config.assert_not_called()
    assert result == 1


# -- Tests for Config Display -- #


@patch(
    "cliff.config.load_config",
    return_value=get_test_base_config(),
)
def test_show_config(mock_load_config, capsys):
    """
    show_config() should print the config and return 0. We'll just check the return code.
    """
    result = show_config()
    captured = capsys.readouterr()
    assert result == 0
    assert "Provider Credentials" in captured.out


@patch("cliff.config.load_config")
def test_show_config_empty(mock_load_config, capsys):
    """
    show_config() should properly display an empty/default configuration
    """
    mock_load_config.return_value = get_test_base_config()

    result = show_config()
    captured = capsys.readouterr()

    assert result == 0
    assert "Not set" in captured.out
    assert "No providers added" in captured.out
    assert "10 Turns" in captured.out
    assert "Ollama Models" not in captured.out
    assert "Preferred Providers" not in captured.out


@patch("cliff.config.load_config")
def test_show_config_full(mock_load_config, capsys):
    """
    show_config() should properly display a configuration with all fields populated
    """
    config = {
        "provider_credentials": {"openai": "123456789", "anthropic": "987654321"},
        "default_model": "gpt-4o",
        "preferred_providers": {"gpt-4o": "openai", "claude-3": "anthropic"},
        "ollama_models": ["llama2", "mistral"],
        "memory_window": 15,
        "timeout_seconds": 20,
    }
    mock_load_config.return_value = config

    result = show_config()
    captured = capsys.readouterr()

    assert result == 0
    assert "gpt-4o" in captured.out
    assert "15 Turns" in captured.out
    assert "20 Seconds" in captured.out
    assert "openai" in captured.out
    assert "anthropic" in captured.out
    assert "llama2" in captured.out
    assert "mistral" in captured.out
    assert "1234...6789" in captured.out
    assert "9876...4321" in captured.out


@patch("cliff.config.load_config")
def test_show_config_partial(mock_load_config, capsys):
    """
    show_config() should properly display a configuration with some fields populated
    """
    config = {
        "provider_credentials": {"openai": "123456789"},
        "default_model": "gpt-4o",
        "preferred_providers": {},
        "ollama_models": ["llama2"],
        "memory_window": 10,
        "timeout_seconds": 20,
    }
    mock_load_config.return_value = config

    result = show_config()
    captured = capsys.readouterr()

    assert result == 0
    assert "gpt-4o" in captured.out
    assert "10 Turns" in captured.out
    assert "20 Seconds" in captured.out
    assert "openai" in captured.out
    assert "llama2" in captured.out
    assert "Preferred Providers" not in captured.out


# -- Tests for Ollama Model Management -- #


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_add_ollama_success(mock_save_config, mock_load_config):
    """
    add_ollama() should add a model to ollama_models and return 0.
    """
    mock_load_config.return_value = get_test_base_config()
    result = add_ollama("llama2")
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_remove_ollama_success(mock_save_config, mock_load_config):
    """
    remove_ollama() should remove a model from ollama_models and return 0.
    """
    config = get_test_config_with_multiple_providers()
    mock_load_config.return_value = config
    result = remove_ollama("llama2")
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_remove_ollama_nonexistent(mock_save_config, mock_load_config):
    """
    remove_ollama() should return 1 if the model is not in ollama_models.
    """
    mock_load_config.return_value = get_test_base_config()
    result = remove_ollama("nonexistent-model")
    mock_save_config.assert_not_called()
    assert result == 1


@patch("cliff.config.add_ollama", return_value=0)
def test_process_config_command_add_ollama(mock_add_ollama):
    """
    process_config_command should invoke add_ollama when "add ollama" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["add", "ollama", "llama2"], llm)
    mock_add_ollama.assert_called_once_with("llama2")
    assert result == 0


@patch("cliff.config.remove_ollama", return_value=0)
def test_process_config_command_remove_ollama(mock_remove_ollama):
    """
    process_config_command should invoke remove_ollama when "remove ollama" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["remove", "ollama", "llama2"], llm)
    mock_remove_ollama.assert_called_once_with("llama2")
    assert result == 0


def test_process_config_command_add_ollama_usage():
    """
    process_config_command with "add ollama" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["add", "ollama"], llm)
    assert result == 1


def test_process_config_command_remove_ollama_usage():
    """
    process_config_command with "remove ollama" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["remove", "ollama"], llm)
    assert result == 1


@patch("l2m2.client.LLMClient.add_provider")
@patch("l2m2.client.LLMClient.set_preferred_providers")
@patch("l2m2.client.LLMClient.add_local_model")
def test_apply_config_with_ollama(
    mock_add_local, mock_set_preferred, mock_add_provider
):
    """
    apply_config() should properly configure local Ollama models.
    """
    config = {
        "provider_credentials": {"openai": "test-key"},
        "default_model": "gpt-4",
        "preferred_providers": {"gpt-4": "openai"},
        "ollama_models": ["llama2", "mistral"],
        "memory_window": 10,
    }
    llm = LLMClient()

    apply_config(config, llm)

    mock_add_local.assert_has_calls(
        [call("llama2", "ollama"), call("mistral", "ollama")]
    )
    mock_add_provider.assert_called_once_with("openai", "test-key")
    mock_set_preferred.assert_called_once_with({"gpt-4": "openai"})


# -- Tests for Misc Command Processing -- #


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


@patch("cliff.config.show_config", return_value=0)
def test_process_config_command_show(mock_show_config):
    """
    process_config_command should invoke show_config when "show" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["show"], llm)
    mock_show_config.assert_called_once()
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


@patch("cliff.config.prefer_add", return_value=0)
def test_process_config_command_prefer_add(mock_prefer_add):
    """
    process_config_command should invoke prefer_add when "prefer" is specified with a model and provider.
    """
    llm = LLMClient()
    result = process_config_command(["prefer", "gpt-4o", "openai"], llm)
    mock_prefer_add.assert_called_once_with("gpt-4o", "openai")
    assert result == 0


@patch("cliff.config.prefer_remove", return_value=0)
def test_process_config_command_prefer_remove(mock_prefer_remove):
    """
    process_config_command should invoke prefer_remove when "prefer remove" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["prefer", "remove", "gpt-4o"], llm)
    mock_prefer_remove.assert_called_once_with("gpt-4o")
    assert result == 0


def test_process_config_command_prefer_usage():
    """
    process_config_command with "prefer" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["prefer", "only-one-arg"], llm)
    assert result == 1


@patch("cliff.config.reset_config", return_value=0)
def test_process_config_command_reset(mock_reset_config):
    """
    process_config_command should invoke reset_config when "reset" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["reset"], llm)
    mock_reset_config.assert_called_once()
    assert result == 0


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_update_memory_window_success(mock_save_config, mock_load_config):
    """
    update_memory_window() should update the memory window size and return 0.
    """
    mock_load_config.return_value = get_test_base_config()
    result = update_memory_window(15)
    mock_save_config.assert_called_once()
    assert result == 0


@patch("cliff.config.save_config")
def test_reset_config_success(mock_save_config):
    """
    reset_config() should reset to default config and return 0.
    """
    result = reset_config()
    mock_save_config.assert_called_once_with(DEFAULT_CONFIG)
    assert result == 0


@patch("cliff.config.update_memory_window", return_value=0)
def test_process_config_command_memory_window(mock_update_memory_window):
    """
    process_config_command should invoke update_memory_window when "memory-window" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["memory-window", "15"], llm)
    mock_update_memory_window.assert_called_once_with(15)
    assert result == 0


def test_process_config_command_memory_window_usage():
    """
    process_config_command with "memory-window" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["memory-window"], llm)
    assert result == 1


@patch("cliff.config.update_timeout", return_value=0)
def test_process_config_command_timeout(mock_update_timeout):
    """
    process_config_command should invoke update_timeout when "timeout" is specified.
    """
    llm = LLMClient()
    result = process_config_command(["timeout", "15"], llm)
    mock_update_timeout.assert_called_once_with(15)
    assert result == 0


def test_process_config_command_timeout_usage():
    """
    process_config_command with "timeout" but incorrect arguments should return 1.
    """
    llm = LLMClient()
    result = process_config_command(["timeout"], llm)
    assert result == 1


@patch("cliff.config.load_config")
@patch("cliff.config.save_config")
def test_update_timeout_success(mock_save_config, mock_load_config):
    """
    update_timeout() should update the timeout seconds and return 0.
    """
    mock_load_config.return_value = get_test_base_config()
    result = update_timeout(30)
    mock_save_config.assert_called_once()
    assert result == 0
