import os
from pathlib import Path
from typing import Any
import sys
from src.audiobook import app, utils
from src.audiobook.yml import YmlReader


def test_audible(monkeypatch: Any, capsys: Any):
    execute(monkeypatch, capsys)


def execute(monkeypatch: Any, capsys: Any):
    asin = "B0G5QKNT1J"
    current_dir = Path(os.getcwd()).resolve()
    yml = current_dir / "metadata.yml"
    cover = current_dir / "cover.jpg"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "audible",
            asin,
            "--locale",
            "fr",
            "--cover",
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    assert utils.file_exists(yml)
    assert utils.file_exists(cover)

    reader = YmlReader(yml).read()
    assert reader.metadata
    assert reader.metadata.title
    assert "Assassin’s Apprentice" in reader.metadata.title

    clear(yml, cover)


def clear(yml: Path, cover: Path):
    utils.remove_file(yml)
    utils.remove_file(cover)
