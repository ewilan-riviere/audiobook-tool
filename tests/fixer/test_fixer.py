from pathlib import Path

from audiobook.audio.fixer.main import AudioFixer
from audiobook.audio.fixer.modules.error_type import ErrorType
import audiobook.utils as utils
from tests.test_files import (
    FIXER_MP3_HEADER,
    FIXER_CHAPTER,
)


def test_mp3_header_missing():
    checker = AudioFixer(FIXER_MP3_HEADER, strict=False).run()
    assert checker.success is True
    assert checker.error_type == ErrorType.REMUX
    output_file = checker.output_path

    checker = AudioFixer(output_file, strict=False).run()
    assert checker.success is True
    assert checker.error_type == ErrorType.NONE

    utils.remove_file(output_file)


def test_chapter():
    checker = AudioFixer(FIXER_CHAPTER, strict=True).run()
    assert checker.success is True
    assert checker.error_type == ErrorType.REMUX

    output_file = checker.output_path

    checker = AudioFixer(output_file, strict=False).run()
    assert checker.success is True
    assert checker.error_type == ErrorType.NONE

    utils.remove_file(output_file)


def test_mp3_header_missing_replaced():
    bk_full_path = Path(FIXER_MP3_HEADER).resolve()
    bk_path = bk_full_path.parent / f"original_{bk_full_path.name}"
    utils.copy_file(FIXER_MP3_HEADER, bk_path)

    checker = AudioFixer(FIXER_MP3_HEADER, strict=False).run(replace_original=True)
    assert checker.success is True
    assert checker.error_type == ErrorType.REMUX
    assert not checker.output_path.exists()

    utils.remove_file(FIXER_MP3_HEADER)
    utils.rename_file(bk_path, bk_full_path.stem)
