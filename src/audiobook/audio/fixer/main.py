"""Fix audio files by detecting specific FFmpeg errors and applying strategies"""

import logging
from pathlib import Path
from typing import Any
from audiobook import utils
from audiobook.audio.fixer.modules import (
    ErrorChecker,
    ErrorType,
    FixerConverter,
    FixerOutput,
    Remuxer,
    Transcoder,
)
from audiobook.audio.reader import AudioReader, AudioType
from audiobook.audio.writer import AudioWriter
from audiobook.common import AutoRepr


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioFixer")


class AudioFixer(AutoRepr):
    """Fix audio files by detecting specific FFmpeg errors and applying strategies"""

    def __init__(self, original_path: Path | str, strict: bool = False):
        self.original_path = Path(original_path).resolve()
        self.strict = strict
        self.error_type = ErrorType.NONE
        self.success: bool = False

        if not self.original_path.exists():
            raise FileNotFoundError(f"{self.original_path} not found.")

        extension = self.original_path.suffix[1:].lower()
        self.audio_type: AudioType = AudioType.from_extension(extension)

        # Check any errors
        checker = ErrorChecker(self.original_path, self.strict).run()
        self.has_errors: bool = checker.has_errors

        # Set output paths
        base_path = self.original_path.parent
        self.m4a_path = (base_path / f"fix_m4a_{self.original_path.name}").with_suffix(
            ".m4a"
        )
        self.transcode_path = (
            base_path / f"fix_transcode_{self.original_path.name}"
        ).with_suffix(".m4a")
        self.output_path: Path = (
            self.original_path.parent / f"fixed_{self.original_path.name}"
        )
        self.replace_original: bool = False

        self.tags: dict[str, Any] = {}
        self.cover: Path | None = None

    def run(self, replace_original: bool = False):
        self.replace_original = replace_original

        if not self.has_errors:
            self.success = True
            return self

        # Keep metadata safe if any
        self._read_metadata()

        # Convert original file to M4A
        FixerConverter(
            self.original_path,
            self.m4a_path,
            self.audio_type,
        ).run()
        if not self.m4a_path.exists():
            raise FileNotFoundError("Error on M4A creation!")

        # Try to remux (fast fix)
        tsuccess = Remuxer(self.m4a_path, self.transcode_path).run()
        if tsuccess:
            self.error_type = ErrorType.REMUX
        else:
            if self.output_path.exists():
                self.output_path.unlink()
            print("Remuxing fails!")
            # If remux fails, try to transcode (heavy fix)
            tsuccess = Transcoder(self.m4a_path, self.transcode_path).run()
            if tsuccess:
                self.error_type = ErrorType.TRANSCODE
            else:
                print("Transcoding fails!")
                # Fix fails, just copy original file as output
                self._fails_rollback()

        # If fix works, convert file to original type
        osuccess: bool = False
        if tsuccess:
            osuccess = FixerOutput(
                self.transcode_path,
                self.output_path,
                self.audio_type,
            ).run()
            if not osuccess:
                print("Output fails!")
                self.error_type = ErrorType.NOT_FIXED

        checker = ErrorChecker(self.output_path, self.strict).run()
        if checker.has_errors:
            print("Errors remaining!")
            print(checker.errors)
            self._fails_rollback()
            self._clean_files()

            return self

        # Write metadata
        self._write_metadata()
        # Replace if need
        self._replace()
        # # Clean temporary files
        self._clean_files()

        if self.error_type not in (ErrorType.NOT_FIXED, ErrorType.UNKNOWN):
            self.success = True
            print("No errors")

        return self

    def _fails_rollback(self):
        self.error_type = ErrorType.NOT_FIXED
        utils.copy_file(self.original_path, self.output_path)

    def _read_metadata(self):
        try:
            reader = AudioReader(self.original_path)
            self.tags = reader.tags.to_dict()
            # TODO save chapters
            self.cover = reader.tags.save_cover(self.original_path.parent)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error when read file {e}")

    def _write_metadata(self):
        if not self.output_path.exists():
            return

        try:
            writer = AudioWriter(self.output_path)
            writer.set_tags(self.tags)
            if self.cover:
                writer.set_cover(self.cover)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error when write file {e}")

    def _replace(self):
        """Remove original path"""
        if not self.replace_original:
            return False

        if self.original_path.exists():
            self.original_path.unlink(missing_ok=True)

        self.output_path.rename(self.original_path)
        # self.output_path = self.original_path

    def _clean_files(self):
        if self.m4a_path:
            self.m4a_path.unlink(missing_ok=True)

        if self.transcode_path:
            self.transcode_path.unlink(missing_ok=True)

        if self.replace_original and self.output_path:
            self.output_path.unlink(missing_ok=True)

        if self.cover:
            self.cover.unlink(missing_ok=True)
