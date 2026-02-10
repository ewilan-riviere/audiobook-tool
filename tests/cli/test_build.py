from typing import Any
import sys
from src.audiobook import app
import src.audiobook.utils as utils


def test_build(monkeypatch: Any, capsys: Any):
    source_path = "./tests/media/the-wall"
    source_path_test = "./tests/media/the-wall-test"
    utils.remove_directory(source_path_test)
    utils.copy_directory(source_path, source_path_test)

    monkeypatch.setattr(
        sys,
        "argv",
        ["audiobook-tool", "build", source_path_test, "--clear"],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    # captured = capsys.readouterr()
    # assert "audiobook-tool" in captured.out
    # assert "Execute command build..." in captured.out
