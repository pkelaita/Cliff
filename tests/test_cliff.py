import pytest
from unittest.mock import patch, mock_open

from cliff.cliff import main, MAN_PAGE, CWD


# -- Tests for Basic Operations -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.update_memory")
def test_main_no_args(
    mock_update_mem, mock_load_mem, mock_apply_config, mock_load_config, monkeypatch
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
def test_main_version_flag(
    mock_update_mem,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
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
def test_main_config_command(
    mock_load_mem, mock_apply_config, mock_load_config, mock_process_config, monkeypatch
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
def test_main_memory_command(
    mock_load_mem, mock_apply_config, mock_load_config, mock_process_memory, monkeypatch
):
    """
    main() with memory command should invoke process_memory_command.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "--memory", "show"])
    main()
    mock_process_memory.assert_called_once()


# -- Tests for Recall Functionality -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.subprocess.run")
def test_main_store_recall(
    mock_subprocess,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
    tmp_path,
):
    """
    main() with recall flag should store command output.
    """
    mock_subprocess.return_value.stdout = "command output"
    mock_subprocess.return_value.stderr = ""
    recall_file = tmp_path / "recall"
    monkeypatch.setattr("cliff.cliff.RECALL_FILE", str(recall_file))
    monkeypatch.setattr("sys.argv", ["cliff.py", "-r", "ls -l"])

    main()

    mock_subprocess.assert_called_once_with(
        "ls -l", shell=True, capture_output=True, text=True
    )

    assert recall_file.read_text().strip() == f"{CWD} $ ls -l\ncommand output"


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
def test_main_show_recall_empty(
    mock_load_mem, mock_apply_config, mock_load_config, monkeypatch, capsys
):
    """
    main() with show-recall flag should handle empty recall file.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "-sr"])
    with patch("builtins.open", mock_open(read_data="")):
        main()
    captured = capsys.readouterr()
    assert "No recalled commands" in captured.out


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
def test_main_show_recall_with_content(
    mock_load_mem, mock_apply_config, mock_load_config, monkeypatch, capsys
):
    """
    main() with show-recall flag should display recall content.
    """
    recall_content = "some/path $ ls\nfile1 file2\n"
    monkeypatch.setattr("sys.argv", ["cliff.py", "-sr"])
    with patch("builtins.open", mock_open(read_data=recall_content)):
        main()
    captured = capsys.readouterr()
    assert recall_content in captured.out


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
def test_main_clear_recall(
    mock_load_mem, mock_apply_config, mock_load_config, monkeypatch, capsys
):
    """
    main() with clear-recall flag should clear recall file.
    """
    monkeypatch.setattr("sys.argv", ["cliff.py", "-cr"])
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        main()
    mock_file().write.assert_called_once_with("")
    captured = capsys.readouterr()
    assert "Cleared recalled commands" in captured.out


# -- Tests for Command Generation -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("cliff.cliff.update_memory")
@patch("l2m2.client.LLMClient.call")
@patch("cliff.cliff.subprocess.run")
@patch("l2m2.client.LLMClient.get_active_models")
@patch("builtins.open", new_callable=mock_open, read_data="man page content")
def test_main_generate_command(
    mock_file,
    mock_get_active_models,
    mock_subprocess,
    mock_llm_call,
    mock_update_mem,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
):
    """
    main() with objective should generate and copy command.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = '{"command": "ls -l"}'
    mock_subprocess.return_value.stdout = "file1 file2"

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with patch("cliff.cliff.subprocess.run") as mock_pbcopy:
        main()
        mock_pbcopy.assert_any_call(["pbcopy"], input="ls -l", text=True)


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_no_active_models(
    mock_get_active_models,
    mock_llm_call,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
    capsys,
):
    """
    main() with no active models should display welcome message.
    """
    mock_load_config.return_value = {"provider_credentials": {}}
    mock_get_active_models.return_value = []
    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(SystemExit) as e:
        main()

    captured = capsys.readouterr()
    assert "Welcome to Cliff" in captured.out
    assert e.value.code == 0


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_invalid_json_response(
    mock_get_active_models,
    mock_llm_call,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
    capsys,
):
    """
    main() should handle invalid JSON response from LLM.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = "invalid json"

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    main()
    captured = capsys.readouterr()
    assert "Error: Invalid JSON response" in captured.out


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_bad_llm_response(
    mock_get_active_models,
    mock_llm_call,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
):
    """
    main() should handle LLM response missing 'command' key.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.return_value = '{"some_other_key": "value"}'

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 1


# -- Tests for Model Selection -- #


@patch("cliff.cliff.load_config")
@patch("cliff.cliff.apply_config")
@patch("cliff.cliff.load_memory")
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_specific_model(
    mock_get_active_models,
    mock_llm_call,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
):
    """
    main() with model flag should use specified model.
    """
    mock_load_config.return_value = {"provider_credentials": {"test": "key"}}
    mock_get_active_models.return_value = ["specific-model"]
    mock_llm_call.return_value = '{"command": "ls -l"}'

    monkeypatch.setattr(
        "sys.argv", ["cliff.py", "--model", "specific-model", "list", "files"]
    )

    main()
    mock_llm_call.assert_called_once()
    assert mock_llm_call.call_args[1]["model"] == "specific-model"


def test_main_model_flag_without_model(monkeypatch):
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
@patch("l2m2.client.LLMClient.call")
@patch("l2m2.client.LLMClient.get_active_models")
def test_main_llm_timeout(
    mock_get_active_models,
    mock_llm_call,
    mock_load_mem,
    mock_apply_config,
    mock_load_config,
    monkeypatch,
    capsys,
):
    """
    main() should handle LLM timeout gracefully.
    """
    mock_load_config.return_value = {
        "default_model": "test-model",
        "provider_credentials": {"test": "key"},
    }
    mock_get_active_models.return_value = ["test-model"]
    mock_llm_call.side_effect = TimeoutError("LLM timeout")

    monkeypatch.setattr("sys.argv", ["cliff.py", "list", "files"])

    with pytest.raises(TimeoutError):
        main()
