"""Fix audio files by detecting specific FFmpeg errors and applying strategies"""

import subprocess
import logging
from pathlib import Path
from typing import Any
from audiobook.audio.reader.main import AudioReader
from audiobook.audio.writer.main import AudioWriter
from audiobook.common.auto_repr import AutoRepr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AudioFixer")


class AudioFixer(AutoRepr):
    """Fix audio files by detecting specific FFmpeg errors and applying strategies"""

    # List of fatal errors that actually impact audio
    CRITICAL_PATTERNS = [
        "corrupt",
        "invalid data",
        "frame sync",
        "decoding error",
        "overread",
        "bitstream",
        "header missing",
        "checksum mismatch",
        "error submitting packet",
        "invalid data found",
        "misdetection possible",
        "conversion failed",
        "invalid audio stream",
    ]

    def __init__(self, file_path: Path | str, strict: bool = False):
        self.file_path = Path(file_path).resolve()
        if not self.file_path.exists():
            raise FileNotFoundError(f"{self.file_path} not found.")

        self.output_path = self.file_path.parent / f"fixed_{self.file_path.name}"
        self.errors = ""
        self.has_errors = False
        self.strict = strict
        self.tags: dict[str, Any] = AudioReader(self.file_path).tags.to_dict()

        self._check_errors()

    def _check_errors(self):
        """Decode to null and analyze the stderr output"""

        # -v info to filter error
        cmd = ["ffmpeg", "-v", "error", "-i", str(self.file_path), "-f", "null", "-"]

        try:
            # NOT set `check=True` here to analyze stderr even fails
            # pylint: disable=subprocess-run-check
            result = subprocess.run(
                cmd,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )
            raw_errors = result.stderr.strip()

            if not raw_errors:
                self.has_errors = False
                self.errors = ""
                return

            if self.strict:
                # Strict mode: if there is text in stderr with -v error, it is an error
                self.has_errors = True
                self.errors = raw_errors
            else:
                # Relaxed mode: check patterns without requiring the “[error]” tag
                critical_lines: list[str] = []
                for line in raw_errors.splitlines():
                    line_lower = line.lower()
                    if any(p in line_lower for p in self.CRITICAL_PATTERNS):
                        critical_lines.append(line)

                self.has_errors = len(critical_lines) > 0
                self.errors = "\n".join(critical_lines)

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.has_errors = True
            self.errors = f"FFmpeg execution failed: {e}"

    def _to_mp3(
        self,
        input_path: Path,
        delete_input: bool = True,
    ) -> Path | None:
        """Converts M4A to MP3"""
        final_mp3 = input_path.with_suffix(".mp3")

        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(input_path),
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",  # High quality (VBR ~190kbps)
            str(final_mp3),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            if delete_input:
                input_path.unlink()
            return final_mp3
        except subprocess.CalledProcessError as e:
            logger.error("Error during final conversion to MP3: %s", e.stderr.decode())
            return None

    def run(self, replace_original: bool = False) -> bool:
        """Repair audio file"""
        if not self.has_errors:
            logger.info("No critical errors detected for %s", self.file_path.name)
            return True

        suffix = self.file_path.suffix.lower()
        working_path = self.output_path.with_suffix(".m4a")

        repair_cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-analyzeduration",
            "20M",
            "-probesize",
            "20M",
            "-i",
            str(self.file_path),
            "-c:a",
            "aac",
            "-q:a",
            "2",
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-vn",
            "-sn",
            "-movflags",
            "+faststart",  # Optimization for m4a/m4b
            str(working_path),
        ]

        try:
            logger.info("Attempting to fix %s via AAC/M4A...", self.file_path.name)
            subprocess.run(repair_cmd, check=True, capture_output=True)

            # Security: file exists and not empty
            if not working_path.exists() or working_path.stat().st_size == 0:
                logger.error("FFmpeg produced an empty or non-existent file.")
                return False

        except subprocess.CalledProcessError as e:
            logger.error(
                "Repair failed: %s", e.stderr.decode() if e.stderr else "Unknown error"
            )
            if working_path.exists():
                working_path.unlink()
            return False

        final_path = working_path
        try:
            if suffix == ".mp3":
                final_path = self._to_mp3(working_path)
            elif suffix == ".m4b":
                m4b_path = working_path.with_suffix(".m4b")
                working_path.rename(m4b_path)
                final_path = m4b_path

            if not final_path or not final_path.exists():
                return False

            if replace_original:
                target_final = self.file_path.with_suffix(final_path.suffix)
                if self.file_path.exists():
                    self.file_path.unlink()
                final_path.rename(target_final)
                logger.info(
                    "File successfully fixed and replaced: %s", target_final.name
                )
                writer = AudioWriter(final_path)
                writer.set_tags(self.tags)

                return True

            logger.info("File fixed: %s", final_path.name)
            writer = AudioWriter(final_path)
            writer.set_tags(self.tags)

            return True

        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Post-processing error: %s", e)
            return False
