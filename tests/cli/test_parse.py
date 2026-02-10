from typing import Any
import tempfile
from pathlib import Path
import sys
from src.audiobook import app
from audiobook.forge import AudiobookForge
import audiobook.utils as utils


def test_parse(monkeypatch: Any, capsys: Any):
    m4b = forge_m4b()
    monkeypatch.setattr(
        sys,
        "argv",
        ["audiobook-tool", "parse", str(m4b)],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command parse..." in captured.out


def forge_m4b():
    mp3_directory = "./tests/media/the-wall"
    mp3_directory_test = "./tests/media/the-wall-test"
    utils.remove_directory(mp3_directory_test)
    utils.copy_directory(mp3_directory, mp3_directory_test)

    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=Path(mp3_directory),
        working_directory=Path(temporary_directory.name),
        clear=True,
    ).run()

    return utils.copy_file(forge.output_path, mp3_directory_test)
