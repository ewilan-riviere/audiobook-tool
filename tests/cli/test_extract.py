from pathlib import Path
from typing import Any
import sys
from audiobook import app, utils
from audiobook.audio.reader.main import AudioReader


def test_extract(monkeypatch: Any, capsys: Any):
    m4b = _build(monkeypatch=monkeypatch)
    _handle(
        monkeypatch=monkeypatch,
        capsys=capsys,
        input_path=m4b,
        audio_type="m4a",
    )

    _handle(
        monkeypatch=monkeypatch,
        capsys=capsys,
        input_path=m4b,
        audio_type="mp3",
    )


def _handle(monkeypatch: Any, capsys: Any, input_path: Path, audio_type: str):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "extract",
            str(input_path),
            "-t",
            audio_type,
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    extracted_files_path = input_path / "extracted_chapters"
    files = utils.get_files(extracted_files_path, audio_type)

    assert len(files) == 5

    first_chapter = files[0]
    reader = AudioReader(first_chapter)
    assert reader.tags.title == "Chapter 1 : In the Flesh? (1)"

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command extract..." in captured.out

    utils.remove_directory(extracted_files_path)


def _build(monkeypatch: Any):
    source_path = "./tests/media/the-wall"
    source_path_test = "./tests/media/the-wall-test"
    utils.remove_directory(source_path_test)
    utils.copy_directory(source_path, source_path_test)

    output_path = "tests/media/output"
    utils.remove_directory(output_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "build",
            source_path_test,
            "--clear",
            "--part-size",
            "1",
            "--output-path",
            output_path,
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    return Path(output_path).resolve()
