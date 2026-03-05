from pathlib import Path
from typing import Any
import sys

import pytest
from audiobook import app
import audiobook.utils as utils
from audiobook.models import ContainerAudiobook
from tests.test_files import (
    AUDIOBOOK_FILES,
    AUDIOBOOK_FILES_IDS,
    OUTPUT_PATH,
    copy_to_output,
)


@pytest.mark.parametrize(
    "path",
    AUDIOBOOK_FILES,
    ids=AUDIOBOOK_FILES_IDS,
)
def test_forge(path: str, monkeypatch: Any):
    files = copy_to_output(path)
    output = Path(f"{OUTPUT_PATH}/forge").resolve()

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "forge",
            str(files),
            "--output-path",
            str(output),
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    container = ContainerAudiobook(output)

    assert container.m4b_file
    assert utils.file_exists(container.m4b_file)

    m4b_files = utils.get_files(output, "m4b")
    assert len(m4b_files) >= 1

    metadata_file = utils.get_file(output, "yml")
    assert metadata_file and metadata_file.exists()

    utils.remove_directory(files)
    utils.remove_directory(output)
