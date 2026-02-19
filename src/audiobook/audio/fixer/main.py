"""Fix audio files by detecting specific FFmpeg errors and applying strategies"""

import json
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from audiobook.audio.reader.main import AudioReader
from audiobook.audio.writer.main import AudioWriter


@dataclass
class RepairResult:
    """Detailed result of the operation"""

    repaired: bool
    path: Path
    strategy: str | None = None
    bitrate: str | None = None
    error: str | None = None


class AudioFixer:
    """Fix audio files by detecting specific FFmpeg errors and applying strategies"""

    def __init__(self, file_path: str | Path):
        self.file_path: Path = Path(file_path).resolve()
        self._remux_errors = ["Referenced QT chapter track not found"]
        self._reencode_errors = [
            "Error submitting packet to decoder",
            "Invalid data found when processing input",
        ]
        self.tags: dict[str, Any] = AudioReader(self.file_path).tags.to_dict()

    def run(self, replace_original: bool = False) -> RepairResult:
        """Analyze and repair if necessary"""
        if self.file_path.name.startswith("fixed_"):
            return RepairResult(False, self.file_path)

        strategy = self._get_strategy()
        if not strategy:
            return RepairResult(False, self.file_path)

        print("🔧 Repair audio files...")
        bitrate = self._get_bitrate() if strategy == "reencode" else None
        return self._repair(strategy, bitrate, replace_original)

    def _get_bitrate(self) -> str | None:
        """Extract the bitrate using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=bit_rate",
                "-of",
                "json",
                str(self.file_path),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            data = json.loads(res.stdout)
            raw_bitrate = data.get("format", {}).get("bit_rate")

            if raw_bitrate and str(raw_bitrate).isdigit():
                return f"{int(raw_bitrate) // 1000}k"
            return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def _get_strategy(self) -> str | None:
        """Analyze FFmpeg's `stderr` to choose the strategy"""
        try:
            res = subprocess.run(
                ["ffmpeg", "-i", str(self.file_path), "-f", "null", "-"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=False,
            )

            # Priority to re-encoding (stream errors)
            if any(err in res.stderr for err in self._reencode_errors):
                return "reencode"

            # Special case MP3
            if res.stderr.count("Header missing") > 5:
                return "reencode"

            # Lightweight strategy (container/chapter errors)
            if any(err in res.stderr for err in self._remux_errors):
                return "remux"

            return None
        except FileNotFoundError as exc:
            raise RuntimeError("The executable ‘ffmpeg’ cannot be found") from exc

    def _fix_tags(self, file_path: Path):
        writer = AudioWriter(file_path)
        writer.set_tags(self.tags)

    def _repair(
        self, strategy: str, bitrate: str | None, replace_original: bool
    ) -> RepairResult:
        """Performs FFmpeg repair"""
        out_p = self.file_path.parent / f"fixed_{self.file_path.name}"
        target_bitrate = bitrate if bitrate else "192k"

        if strategy == "remux":
            audio_opts = ["-c:a", "copy"]
        else:
            codec = "libmp3lame" if self.file_path.suffix.lower() == ".mp3" else "aac"
            audio_opts = ["-c:a", codec, "-b:a", target_bitrate]

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.file_path),
            "-map",
            "0:a",
            *audio_opts,
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-vn",
            str(out_p),
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            if replace_original:
                out_p.replace(self.file_path)
                self._fix_tags(self.file_path)

                return RepairResult(
                    True,
                    self.file_path,
                    strategy,
                    target_bitrate if strategy == "reencode" else None,
                )

            self._fix_tags(out_p)
            return RepairResult(
                True,
                out_p,
                strategy,
                target_bitrate if strategy == "reencode" else None,
            )

        except subprocess.CalledProcessError as e:
            self._fix_tags(self.file_path)
            return RepairResult(
                False,
                self.file_path,
                error=f"FFmpeg error: {e.stderr}",
            )
        except OSError as e:
            self._fix_tags(self.file_path)
            return RepairResult(
                False,
                self.file_path,
                error=f"System error: {e.strerror}",
            )
