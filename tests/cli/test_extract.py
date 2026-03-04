from pathlib import Path
import tempfile
from typing import Any
import sys
from audiobook import app, utils
from audiobook.audio.reader.main import AudioReader
from audiobook.forge.main import AudiobookForge
from tests.test_files import (
    AUDIOBOOK_MP3,
    AUDIOBOOK_M4A,
    AUDIOBOOK_MP3_FILES,
    AUDIOBOOK_M4A_FILES,
    copy_to_output,
    OUTPUT_PATH,
)


# def test_extract(monkeypatch: Any, capsys: Any):
#     m4b = _build(monkeypatch=monkeypatch)
#     _handle(
#         monkeypatch=monkeypatch,
#         capsys=capsys,
#         input_path=m4b,
#         audio_type="m4a",
#     )

#     _handle(
#         monkeypatch=monkeypatch,
#         capsys=capsys,
#         input_path=m4b,
#         audio_type="mp3",
#     )


# def _handle(monkeypatch: Any, capsys: Any, input_path: Path, audio_type: str):
#     monkeypatch.setattr(
#         sys,
#         "argv",
#         [
#             "audiobook-tool",
#             "extract",
#             str(input_path),
#             "-t",
#             audio_type,
#         ],
#     )

#     try:
#         app.main()
#     except SystemExit as e:
#         assert e.code == 0

#     extracted_files_path = input_path / "extracted_chapters"
#     files = utils.get_files(extracted_files_path, audio_type)

#     assert len(files) == 5

#     first_chapter = files[0]
#     reader = AudioReader(first_chapter)
#     assert reader.tags.title == "Chapter 1 : In the Flesh? (1)"

#     captured = capsys.readouterr()
#     assert "audiobook-tool" in captured.out
#     assert "Execute command extract..." in captured.out

#     utils.remove_directory(extracted_files_path)


def test_extract(monkeypatch: Any):
    files = copy_to_output(AUDIOBOOK_MP3_FILES)
    print(files)

    temporary_directory = tempfile.TemporaryDirectory()
    forge = AudiobookForge(
        source_path=files,
        working_directory=Path(temporary_directory.name),
        clear=True,
    )

    # source_path = "./tests/media/the-wall"
    # source_path_test = "./tests/media/the-wall-test"
    # utils.remove_file(source_path_test)
    # utils.copy_directory(source_path, source_path_test)

    # output_path = "tests/media/output"
    # utils.remove_directory(output_path)

    # monkeypatch.setattr(
    #     sys,
    #     "argv",
    #     [
    #         "audiobook-tool",
    #         "build",
    #         source_path_test,
    #         "--clear",
    #         "--part-size",
    #         "1",
    #         "--output-path",
    #         output_path,
    #     ],
    # )

    # try:
    #     app.main()
    # except SystemExit as e:
    #     assert e.code == 0

    # return Path(output_path).resolve()

    utils.remove_directory(files)
