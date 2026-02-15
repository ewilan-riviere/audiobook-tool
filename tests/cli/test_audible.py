import os
from pathlib import Path
from typing import Any
import sys
from audiobook import app, utils
from audiobook.yml import YmlReader


def test_audible(monkeypatch: Any, capsys: Any):
    asin = "B0G5QKNT1J"
    current_dir = Path(os.getcwd()).resolve()
    metadata_yml_path = current_dir / "metadata.yml"
    cover_path = current_dir / "cover.jpg"

    utils.remove_file(metadata_yml_path)
    utils.remove_file(cover_path)

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

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command audible..." in captured.out

    assert utils.file_exists(metadata_yml_path)
    assert utils.file_exists(cover_path)

    reader = YmlReader(metadata_yml_path).read()
    assert reader.metadata
    assert reader.metadata.title == "Assassin’s Apprentice"

    utils.remove_file(metadata_yml_path)
    utils.remove_file(cover_path)
