from typing import Any
import sys
from src.audiobook import app


def test_build(monkeypatch: Any, capsys: Any):
    monkeypatch.setattr(
        sys,
        "argv",
        ["audiobook-tool", "build", "./tests/media/the-wall"],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    # captured = capsys.readouterr()
    # assert "audiobook-tool" in captured.out
    # assert "Execute command build..." in captured.out
