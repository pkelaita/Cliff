import pytest
from unittest.mock import patch
from cliff.cliff import main


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["-r", "ls", "-al"],
        ["-vr"],
        ["-cr"],
        ["some", "multi", "word", "objective"],
    ],
)
@patch("l2m2.client.LLMClient.call")
def test_cliff_runs_without_errors(mock_call, args, monkeypatch):
    mock_call.return_value = '{"command": "echo Hello World"}'

    monkeypatch.setattr("sys.argv", ["cliff.py"] + args)

    try:
        main()
    except SystemExit as e:
        assert e.code == 0
