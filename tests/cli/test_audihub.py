from typing import Any
from .test_audible import execute


def test_audihub(monkeypatch: Any, capsys: Any):
    execute(monkeypatch, capsys)
