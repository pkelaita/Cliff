from unittest.mock import patch, mock_open

from cliff.notepad import (
    clear_notepad,
    load_notepad,
    run_notepad,
    show_notepad,
    process_notepad_command,
    NOTEPAD_FILE,
)


# -- Tests for Basic Notepad Operations -- #


@patch("builtins.open", new_callable=mock_open)
def test_clear_notepad(mock_file):
    """
    clear_notepad() should open the notepad file in write mode and write an empty string.
    """
    clear_notepad()
    mock_file.assert_called_once_with(NOTEPAD_FILE, "w")
    mock_file().write.assert_called_once_with("")


@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("cliff.notepad.clear_notepad")
@patch("builtins.open", new_callable=mock_open, read_data="test content")
def test_load_notepad_file_not_exist(
    mock_file, mock_clear_notepad, mock_makedirs, mock_path_exists
):
    """
    If notepad file doesn't exist, load_notepad() should create it and return empty string.
    """
    result = load_notepad()
    mock_makedirs.assert_called_once()
    mock_clear_notepad.assert_called_once()
    assert result == "test content"


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="test content")
def test_load_notepad_file_exists(mock_file, mock_path_exists):
    """
    If notepad file exists, load_notepad() should read and return its contents.
    """
    result = load_notepad()
    mock_file.assert_called_once_with(NOTEPAD_FILE, "r")
    assert result == "test content"


# -- Tests for Notepad Command Execution -- #


@patch("subprocess.run")
@patch("builtins.open", new_callable=mock_open)
@patch("builtins.print")
def test_run_notepad_success(mock_print, mock_file, mock_subprocess):
    """
    run_notepad() should execute command and log output to notepad file.
    """
    mock_subprocess.return_value.stdout = "command output\n"
    mock_subprocess.return_value.stderr = ""

    run_notepad("test command")

    mock_subprocess.assert_called_once_with(
        "test command", shell=True, capture_output=True, text=True
    )
    mock_file.assert_called_once_with(NOTEPAD_FILE, "a")
    mock_file().write.assert_called_once()
    assert "command output" in mock_print.call_args_list[0][0][0]


@patch("subprocess.run")
@patch("builtins.open", new_callable=mock_open)
@patch("builtins.print")
def test_run_notepad_with_stderr(mock_print, mock_file, mock_subprocess):
    """
    run_notepad() should capture and log both stdout and stderr.
    """
    mock_subprocess.return_value.stdout = "standard output\n"
    mock_subprocess.return_value.stderr = "error output\n"

    run_notepad("test command")

    mock_subprocess.assert_called_once()
    mock_file.assert_called_once_with(NOTEPAD_FILE, "a")
    mock_file().write.assert_called_once()
    output = mock_print.call_args_list[0][0][0]
    assert "standard output" in output
    assert "error output" in output


# -- Tests for Notepad Display -- #


@patch("builtins.open", new_callable=mock_open, read_data="test content")
def test_show_notepad_with_content(mock_file, capsys):
    """
    show_notepad() should display notepad contents when not empty.
    """
    show_notepad()
    mock_file.assert_called_once_with(NOTEPAD_FILE, "r")
    captured = capsys.readouterr()
    assert "Notepad contents:" in captured.out
    assert "test content" in captured.out


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_show_notepad_empty(mock_file, capsys):
    """
    show_notepad() should display appropriate message when notepad is empty.
    """
    show_notepad()
    mock_file.assert_called_once_with(NOTEPAD_FILE, "r")
    captured = capsys.readouterr()
    assert "Notepad is empty" in captured.out


# -- Tests for Command Processing -- #


def test_process_notepad_command_no_args():
    """
    process_notepad_command() should return 1 and show usage when no args provided.
    """
    result = process_notepad_command([])
    assert result == 1


def test_process_notepad_command_invalid():
    """
    process_notepad_command() should return 1 and show usage for invalid command.
    """
    result = process_notepad_command(["invalid"])
    assert result == 1


@patch("cliff.notepad.run_notepad")
def test_process_notepad_command_run(mock_run_notepad):
    """
    process_notepad_command() should invoke run_notepad for 'run' command.
    """
    result = process_notepad_command(["run", "test command"])
    mock_run_notepad.assert_called_once_with("test command")
    assert result == 0


def test_process_notepad_command_run_no_command():
    """
    process_notepad_command() should return 1 for 'run' without command.
    """
    result = process_notepad_command(["run"])
    assert result == 1


@patch("cliff.notepad.show_notepad")
def test_process_notepad_command_show(mock_show_notepad):
    """
    process_notepad_command() should invoke show_notepad for 'show' command.
    """
    result = process_notepad_command(["show"])
    mock_show_notepad.assert_called_once()
    assert result == 0


@patch("cliff.notepad.clear_notepad")
def test_process_notepad_command_clear(mock_clear_notepad):
    """
    process_notepad_command() should invoke clear_notepad for 'clear' command.
    """
    result = process_notepad_command(["clear"])
    mock_clear_notepad.assert_called_once()
    assert result == 0
