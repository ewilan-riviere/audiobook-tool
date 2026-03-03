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
        ["audiobook-tool", "parse", str(m4b.parent)],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command parse..." in captured.out


def forge_m4b():
    source_directory = Path("./tests/media/the-wall").resolve()
    source_directory_test = Path("./tests/media/the-wall-test").resolve()
    utils.remove_directory(source_directory_test)
    utils.copy_directory(source_directory, source_directory_test)

    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=Path(source_directory_test),
        working_directory=Path(temporary_directory.name),
        clear=True,
    ).run()

    if not forge.output_path:
        raise FileNotFoundError(f"File not found at path {str(forge.output_path)}")

    return utils.copy_file(forge.output_path, source_directory_test)
