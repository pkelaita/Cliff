from unittest.mock import patch, Mock, mock_open
import pytest

from cliff.console import LoadingAnimation, cliff_print, resource_print


# -- Tests for Loading Animation -- #


@patch("threading.Thread")
def test_loading_animation_context_manager(mock_thread):
    """
    LoadingAnimation should work as a context manager.
    """
    mock_thread_instance = Mock()
    mock_thread.return_value = mock_thread_instance

    with LoadingAnimation(delay=0.01) as anim:
        assert not anim.stop_event.is_set()
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    assert anim.stop_event.is_set()
    mock_thread_instance.join.assert_called_once()


@patch("threading.Thread")
def test_loading_animation_manual_control(mock_thread):
    """
    LoadingAnimation should work with manual start/stop.
    """
    mock_thread_instance = Mock()
    mock_thread.return_value = mock_thread_instance

    anim = LoadingAnimation(delay=0.01)

    anim.start()
    assert not anim.stop_event.is_set()
    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()

    anim.stop()
    assert anim.stop_event.is_set()
    mock_thread_instance.join.assert_called_once()


@patch("threading.Thread")
def test_loading_animation_multiple_starts(mock_thread):
    """
    LoadingAnimation should handle multiple start calls by creating new threads.
    """
    mock_thread_instances = [Mock(), Mock()]
    mock_thread.side_effect = mock_thread_instances

    anim = LoadingAnimation(delay=0.01)

    # First start
    anim.start()
    assert mock_thread.call_count == 1
    mock_thread_instances[0].start.assert_called_once()

    # Second start - should create new thread
    anim.start()
    assert mock_thread.call_count == 2
    mock_thread_instances[1].start.assert_called_once()

    # Verify current thread is the second one
    assert anim.thread == mock_thread_instances[1]

    # Stop should only affect current thread
    anim.stop()
    mock_thread_instances[1].join.assert_called_once()
    mock_thread_instances[0].join.assert_not_called()


def test_loading_animation_custom_delay():
    """
    LoadingAnimation should accept custom delay value.
    """
    custom_delay = 0.1
    anim = LoadingAnimation(delay=custom_delay)
    assert anim.delay == custom_delay


# -- Tests for Console Output -- #


@patch("cliff.console.console.print")
def test_cliff_print(mock_console_print):
    """
    cliff_print() should format message with Cliff prefix.
    """
    message = "test message"
    cliff_print(message)

    mock_console_print.assert_called_once_with(
        "[cyan][Cliff][/cyan]", highlight=False, end=" "
    )


# -- Tests for Resource Printing -- #


@pytest.fixture
def mock_file():
    """Fixture that mocks a file containing 'test content'"""
    with patch("builtins.open", mock_open(read_data="test content")) as mock_file:
        yield mock_file


@patch("cliff.console.subprocess.run")
def test_resource_print(mock_subprocess_run, mock_file):
    """
    resource_print() should print the content of a file.
    """
    resource_print("test_file.txt")

    mock_file.assert_called_once_with("test_file.txt", "r")
    mock_subprocess_run.assert_called_once_with(
        ["less", "-R", "-X", "-J", "-F"], input="test content".encode(), check=True
    )


@patch("cliff.console.subprocess.run")
def test_resource_print_with_fn(mock_subprocess_run, mock_file):
    """
    resource_print() should apply a function to the content if provided.
    """
    resource_print("test_file.txt", lambda x: x.upper())

    mock_file.assert_called_once_with("test_file.txt", "r")
    mock_subprocess_run.assert_called_once_with(
        ["less", "-R", "-X", "-J", "-F"], input="TEST CONTENT".encode(), check=True
    )
