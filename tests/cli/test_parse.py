from typing import Any
import sys

import pytest
from src.audiobook import app
import audiobook.utils as utils
from tests.test_files import (
    AUDIOBOOK_FILES,
    AUDIOBOOK_FILES_IDS,
    create_audiobook,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_parse(path: str, monkeypatch: Any, capsys: Any):
    audiobook = create_audiobook(monkeypatch, path)
    monkeypatch.setattr(
        sys,
        "argv",
        ["audiobook-tool", "parse", str(audiobook)],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    utils.remove_directory(audiobook)
