from pathlib import Path
import sys
from typing import Any
from audiobook import app
from audiobook import utils


RAW_MP3_FILE = "tests/media/raw/mp3-file.mp3"
RAW_M4B_AAC_FILE = "tests/media/raw/m4b-aac-file.m4b"
RAW_M4B_ALAC_FILE = "tests/media/raw/m4b-alac-file.m4b"
RAW_M4A_AAC_FILE = "tests/media/raw/m4a-aac-file.m4a"
RAW_M4A_ALAC_FILE = "tests/media/raw/m4a-alac-file.m4a"

FIXER_MP3_HEADER = "tests/media/fixer/header-missing.mp3"
FIXER_CHAPTER = "tests/media/fixer/chapter.m4b"

RAW_FILES = [
    RAW_MP3_FILE,
    RAW_M4B_AAC_FILE,
    RAW_M4B_ALAC_FILE,
    RAW_M4A_AAC_FILE,
    RAW_M4A_ALAC_FILE,
]
RAW_FILES_IDS = [
    "RAW_MP3",
    "RAW_M4B_AAC",
    "RAW_M4B_ALAC",
    "RAW_M4A_AAC",
    "RAW_M4A_ALAC",
]


AUDIOBOOK_MP3 = "tests/media/audiobook/audiobook-mp3.m4b"
AUDIOBOOK_M4A = "tests/media/audiobook/audiobook-m4a.m4b"
AUDIOBOOKS = [AUDIOBOOK_MP3, AUDIOBOOK_M4A]
AUDIOBOOKS_IDS = ["AUDIOBOOK_MP3", "AUDIOBOOK_M4A"]
AUDIOBOOK_MP3_FILES = "tests/media/audiobook/mp3"
AUDIOBOOK_M4A_FILES = "tests/media/audiobook/m4a"
AUDIOBOOK_FILES = [AUDIOBOOK_MP3_FILES, AUDIOBOOK_M4A_FILES]
AUDIOBOOK_FILES_IDS = ["MP3", "M4A"]

COVER_ORIGINAL = "tests/media/covers/cover-original.jpg"
COVER_ORIGINAL_PNG = "tests/media/covers/cover-original.png"
COVER_NEW = "tests/media/covers/cover-new.jpg"

OUTPUT_PATH = "tests/media/output"

YML_TEMPLATE = "metadata.template.yml"


def output_path(file_path: str) -> Path:
    """Get full output path"""
    new_path = f"{OUTPUT_PATH}/{file_path}"
    new_path = Path(new_path).resolve()

    return new_path


def copy_to_output(path: Path | str) -> Path:
    """Copy directory or file to `OUTPUT_PATH`"""
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()
    if path.is_dir():
        return utils.copy_directory(path, output_path(path.name))

    if path.is_file():
        return utils.copy_file(path, output_path(path.name))

    raise FileNotFoundError(f"Error on {path}")


def create_audiobook(
    monkeypatch: Any,
    source_files: str,
    name: str = "audiobook",
) -> Path:
    """Create audiobook in `OUTPUT_PATH` and return `Path`"""
    output = f"{OUTPUT_PATH}/{name}"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audiobook-tool",
            "build",
            source_files,
            "--clear",
            "--part-size",
            "1",
            "--output-path",
            output,
        ],
    )

    try:
        app.main()
    except SystemExit as e:
        assert e.code == 0

    return Path(output).resolve()
