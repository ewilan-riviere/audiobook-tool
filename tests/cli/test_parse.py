from typing import Any
import sys
from src.audiobook import app


def test_parse(monkeypatch: Any, capsys: Any):
    monkeypatch.setattr(
        sys,
        "argv",
        ["audiobook-tool", "parse", "/Users/ewilan/Downloads/M4B_no_cover.m4b"],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command parse..." in captured.out
