from typing import Any
import sys
from audiobook import app
import audiobook.utils as utils
from audiobook.models import ContainerAudiobook


def test_forge(monkeypatch: Any, capsys: Any):
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
            "forge",
            source_path_test,
            "--output-path",
            output_path,
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    container = ContainerAudiobook(output_path)

    assert container.m4b_file
    assert utils.file_exists(container.m4b_file)

    captured = capsys.readouterr()
    assert "audiobook-tool" in captured.out
    assert "Execute command forge..." in captured.out
