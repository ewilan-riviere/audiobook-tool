from pathlib import Path
from typing import Any
import sys

import pytest
from audiobook import app
import audiobook.utils as utils
from audiobook.audio import AudioReader
from audiobook.models import ContainerAudiobook
from tests.test_files import (
    AUDIOBOOK_FILES,
    AUDIOBOOK_FILES_IDS,
    copy_to_output,
    OUTPUT_PATH,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_build(path: str, monkeypatch: Any, capsys: Any):
    files_path = copy_to_output(path)
    output_temp = Path(f"{OUTPUT_PATH}/audiobook").resolve()
    utils.remove_directory(output_temp)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "build",
            str(files_path),
            "--part-size",
            "1",
            "--clear",
            "--output-path",
            str(output_temp),
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    container = ContainerAudiobook(output_temp)
    reader = AudioReader(str(container.m4b_file))

    assert reader.tags.title == "The Wall - Part 01"
    assert reader.tags.album == "The Wall Anthology 01: The Wall"

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out

    utils.remove_directory(files_path)
    utils.remove_directory(output_temp)
