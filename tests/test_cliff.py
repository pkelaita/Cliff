import pytest
from unittest.mock import patch, mock_open

from l2m2.exceptions import LLMTimeoutError

from cliff.cliff import main, MAN_PAGE


# -- Tests for Basic Operations -- #


@pytest.fixture
def mock_pbcopy():
    """Mock the pbcopy subprocess call"""
    with patch("cliff.cliff.subprocess.run") as mock:
        yield mock


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.update_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_no_args(
    mock_loading,
    mock_update_mem,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with no args should display man page and return.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py"])
    with patch("builtins.open", mock_open(read_data="man page content")) as mock_file:
        main()
        mock_file.assert_called_once_with(MAN_PAGE, "r")


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.update_memory")
@patch("cliff.cliff.__version__", "1.0.0")
@patch("cliff.cliff.LoadingAnimation")
def test_main_version_flag(
    mock_loading,
    mock_update_mem,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
    capsys,
):
    """
    main() with version flag should display version and return.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "-v"])
    main()
    captured = capsys.readouterr()
    assert "Version 1.0.0" in captured.out


# -- Tests for Config Integration -- #


@patch("cliff.cliff.process_config_command", return_value=0)
@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_config_command(
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_process_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with config command should invoke process_config_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--config", "show"])
    main()
    mock_process_config.assert_called_once()


# -- Tests for Memory Integration -- #


@patch("cliff.cliff.process_memory_command", return_value=0)
@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_memory_command(
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_process_memory,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with memory command should invoke process_memory_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--memory", "show"])
    main()
    mock_process_memory.assert_called_once()


# -- Tests for Notepad Functionality -- #


@patch("cliff.cliff.process_notepad_command", return_value=0)
@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_show_notepad(
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_process_notepad,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with notepad command should invoke process_notepad_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--notepad", "show"])
    main()
    mock_process_notepad.assert_called_once()


@patch("cliff.cliff.process_notepad_command", return_value=0)
@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_run_notepad(
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_process_notepad,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with notepad command should invoke process_notepad_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--notepad", "run", "ls -l"])
    main()
    mock_process_notepad.assert_called_once()


@patch("cliff.cliff.process_notepad_command", return_value=0)
@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
def test_main_clear_notepad(
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_process_notepad,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with notepad command should invoke process_notepad_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--notepad", "clear"])
    main()
    mock_process_notepad.assert_called_once()


# -- Tests for Misc Options -- #


@patch("cliff.cliff.clear_memory")
@patch("cliff.cliff.clear_notepad")
def test_main_clear_command(
    mock_clear_memory,
    mock_clear_notepad,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with clear command should invoke clear_memory and clear_notepad.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--clear"])
    main()
    mock_clear_memory.assert_called_once()
    mock_clear_notepad.assert_called_once()


# -- Tests for Command Generation -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("cliff.cliff.resource_print")
def test_main_no_default_model(
    mock_resource_print,
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() should display help message and exit when no default model is set
    and no model is specified via command line.
    """
    mock_load_config.return_value = {
        "default_model": None,
        "provider_credentials": {"test": "key"},
        "memory_window": 10,
        "timeout_seconds": 30,
    }
    mock_get_active_models.return_value = ["test-model"]

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(SystemExit) as e:
        main()

    mock_resource_print.assert_called_once()
    called_path = mock_resource_print.call_args[0][0]
    assert called_path.endswith("resources/ambiguous_model.txt")
    assert e.value.code == 0


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("cliff.cliff.LoadingAnimation")
@patch("builtins.open", new_callable=mock_open, read_data="man page content")
def test_main_generate_command(
    mock_file,
    mock_loading,
    mock_get_active_models,
    mock_llm_call,
    mock_update_mem,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with objective should generate and copy command.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
        "memory_window": 10,
        "timeout_seconds": 30,
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = '{"command": "ls -l"}'

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])
    main()
    mock_pbcopy.assert_called_once_with(["pbcopy"], input="ls -l", text=True)


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("cliff.cliff.resource_print")
def test_main_no_active_models(
    mock_resource_print,
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with no active models should display welcome message.
    """
    mock_load_config.return_value = {
        "provider_credentials": {},
        "timeout_seconds": 30,
        "memory_window": 10,
    }
    mock_get_active_models.return_value = []
    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(SystemExit) as e:
        main()

    mock_resource_print.assert_called_once()
    called_path = mock_resource_print.call_args[0][0]
    assert called_path.endswith("resources/no_active_models.txt")
    assert e.value.code == 0


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("cliff.cliff.resource_print")
def test_main_invalid_json_response(
    mock_resource_print,
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() should handle invalid JSON response from LLM.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
        "timeout_seconds": 30,
        "memory_window": 10,
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = "invalid json"

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    main()
    mock_resource_print.assert_called_once()
    called_path = mock_resource_print.call_args[0][0]
    assert called_path.endswith("resources/malformed_response.txt")


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("cliff.cliff.resource_print")
def test_main_bad_llm_response(
    mock_resource_print,
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() should handle LLM response missing 'command' key.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
        "timeout_seconds": 30,
        "memory_window": 10,
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = '{"some_other_key": "value"}'

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    main()
    mock_resource_print.assert_called_once()
    called_path = mock_resource_print.call_args[0][0]
    assert called_path.endswith("resources/malformed_response.txt")


# -- Tests for Model Selection -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_specific_model(
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
):
    """
    main() with model flag should use specified model.
    """
    mock_load_config.return_value = {
        "provider_credentials": {"test": "key"},
        "default_model": "some-model",
        "timeout_seconds": 30,
        "memory_window": 10,
    }
    mock_get_active_models.return_value = ["specific-model"]
    mock_llm_call.return_value = '{"command": "ls -l"}'

    monkeypatch.setattr(
        "sys.argv", ["cliff.py", "--model", "specific-model", "list", "files"]
    )

    main()
    mock_llm_call.assert_called_once()
    assert mock_llm_call.call_args[1]["model"] == "specific-model"


def test_main_model_flag_without_model(mock_pbcopy, monkeypatch):
    """
    main() with model flag but no model specified should exit with error.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--model"])

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1


# -- Tests for Error Handling -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.LoadingAnimation")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_llm_timeout(
    mock_get_active_models,
    mock_llm_call,
    mock_loading,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    mock_pbcopy,
    monkeypatch,
    capsys,
):
    """
    main() should handle LLM timeout gracefully.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
        "timeout_seconds": 30,
        "memory_window": 10,
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.side_effect = LLMTimeoutError("LLM timeout")

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(SystemExit) as e:
        main()
    captured = capsys.readouterr()
    assert "LLM call timed out" in captured.out
    assert e.value.code == 1
