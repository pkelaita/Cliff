from unittest.mock import patch, mock_open

from l2m2.memory import ChatMemory

from cliff.memory import (
    load_memory,
    update_memory,
    clear_memory,
    show_memory,
    process_memory_command,
    MEMORY_FILE,
    _truncate,
)


# -- Tests for Memory File Operations -- #


@patch("os.path.exists", return_value=False)
@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open, read_data="[]")
def test_load_memory_file_not_exist(mock_file, mock_makedirs, mock_path_exists):
    """
    If memory file doesn't exist, load_memory() should create an empty memory file
    and return 0.
    """
    mem = ChatMemory()
    result = load_memory(mem, 10)
    mock_makedirs.assert_called_once()
    mock_file.assert_any_call(MEMORY_FILE, "w")
    assert result == 0


@patch("os.path.exists", return_value=True)
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data='[{"role": "user", "content": "test message"}, {"role": "assistant", "content": "{\\"command\\": \\"test response\\"}"}]',
)
def test_load_memory_file_exists(mock_file, mock_path_exists):
    """
    If memory file exists, load_memory() should read it and populate ChatMemory.
    """
    mem = ChatMemory()
    result = load_memory(mem, 10)
    mock_file.assert_called_once_with(MEMORY_FILE, "r")
    assert result == 0
    messages = mem.unpack("role", "content", "user", "assistant")
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "test message"


@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
def test_update_memory(mock_json_dump, mock_file):
    """
    update_memory() should dump the ChatMemory contents to the memory file.
    """
    mem = ChatMemory()
    mem.add_user_message("test message")
    mem.add_agent_message('{"command": "test response"}')

    result = update_memory(mem, 10)

    mock_file.assert_called_once_with(MEMORY_FILE, "w")
    mock_json_dump.assert_called_once()
    assert result == 0


@patch("builtins.open", new_callable=mock_open)
def test_clear_memory(mock_file):
    """
    clear_memory() should write an empty list to the memory file.
    """
    clear_memory()
    mock_file.assert_called_once_with(MEMORY_FILE, "w")
    mock_file().write.assert_called_once_with("[]")


# -- Tests for Memory Display -- #


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="""[
        {"role": "user", "content": "first message"},
        {"role": "assistant", "content": "{\\"command\\": \\"first response\\"}"},
        {"role": "user", "content": "second message"},
        {"role": "assistant", "content": "{\\"command\\": \\"second response\\"}"},
        {"role": "user", "content": "third message"},
        {"role": "assistant", "content": "{\\"command\\": \\"third response\\"}"}
    ]""",
)
def test_show_memory(mock_file, capsys):
    """
    show_memory() should print the memory contents in a readable format.
    """
    result = show_memory(10)
    captured = capsys.readouterr()

    assert result == 0
    assert "User:  first message" in captured.out
    assert "Cliff: first response" in captured.out
    assert "User:  second message" in captured.out
    assert "Cliff: second response" in captured.out
    assert "User:  third message" in captured.out
    assert "Cliff: third response" in captured.out


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="""[
        {"role": "user", "content": "first message"},
        {"role": "assistant", "content": "{\\"command\\": \\"first response\\"}"},
        {"role": "user", "content": "second message"},
        {"role": "assistant", "content": "{\\"command\\": \\"second response\\"}"},
        {"role": "user", "content": "third message"},
        {"role": "assistant", "content": "{\\"command\\": \\"third response\\"}"}
    ]""",
)
def test_show_memory_truncated(mock_file, capsys):
    """
    show_memory() should truncate the memory contents to the window size.
    """
    result = show_memory(2)
    captured = capsys.readouterr()

    assert result == 0
    assert "User:  first message" not in captured.out
    assert "Cliff: first response" not in captured.out
    assert "User:  second message" in captured.out
    assert "Cliff: second response" in captured.out
    assert "User:  third message" in captured.out
    assert "Cliff: third response" in captured.out


@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data="[]",
)
def test_show_memory_empty(mock_file, capsys):
    """
    show_memory() should handle empty memory gracefully.
    """
    result = show_memory(10)
    captured = capsys.readouterr()

    assert result == 0
    assert "Memory is empty" in captured.out


# -- Tests for Memory Window Management -- #


def test_truncate_normal():
    """
    _truncate() should keep the last n*2 items where n is the window size.
    """
    data = [{"id": i} for i in range(10)]
    result = _truncate(data, 3)
    assert len(result) == 6
    assert result[0]["id"] == 4
    assert result[-1]["id"] == 9


def test_truncate_small_data():
    """
    _truncate() should not modify data smaller than window size * 2.
    """
    data = [{"id": i} for i in range(3)]
    result = _truncate(data, 3)
    assert len(result) == 3
    assert result == data


def test_truncate_zero_window():
    """
    _truncate() should return empty list for window size 0.
    """
    data = [{"id": i} for i in range(5)]
    result = _truncate(data, 0)
    assert len(result) == 0


def test_truncate_negative_window():
    """
    _truncate() should raise ValueError for negative window size.
    """
    data = [{"id": i} for i in range(5)]
    try:
        _truncate(data, -1)
        assert False, "Expected ValueError"
    except ValueError:
        pass


# -- Tests for Command Processing -- #


@patch("cliff.memory.show_memory", return_value=0)
def test_process_memory_command_show(mock_show_memory):
    """
    process_memory_command should invoke show_memory when "show" is specified.
    """
    result = process_memory_command(["show"], 10)
    mock_show_memory.assert_called_once()
    assert result == 0


@patch("cliff.memory.clear_memory")
def test_process_memory_command_clear(mock_clear_memory):
    """
    process_memory_command should invoke clear_memory when "clear" is specified.
    """
    result = process_memory_command(["clear"], 10)
    mock_clear_memory.assert_called_once()
    assert result == 0


def test_process_memory_command_invalid():
    """
    process_memory_command with an invalid command should return 1.
    """
    result = process_memory_command(["invalid"], 10)
    assert result == 1


def test_process_memory_command_empty():
    """
    process_memory_command with no command should return 1.
    """
    result = process_memory_command([], 10)
    assert result == 1
