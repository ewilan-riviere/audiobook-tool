"""Convert MP3 to M4A, M4B/M4A to M4A and clean all tags and cover"""

from pathlib import Path
import subprocess

from audiobook.audio.reader import AudioType


class FixerConverter:
    """Convert MP3 to M4A, M4B/M4A to M4A and clean all tags and cover"""

    def __init__(
        self,
        input_path: Path,
        output_path: Path,
        audio_type: AudioType,
    ) -> None:
        self.input_path: Path = input_path
        self.output_path: Path = output_path
        self.audio_type: AudioType = audio_type

    def run(self):
        """Execute conversion"""

        self._clean_output()
        if self.audio_type == AudioType.MP3:
            self._mp3_to_m4a()
        elif self.audio_type in (AudioType.M4B, AudioType.M4A):
            self._clean_m4a()
        else:
            print(f"Extension {self.audio_type.value} not handled!")

        return self

    def _clean_output(self):
        if self.output_path.exists():
            self.output_path.unlink()

    def _mp3_to_m4a(self) -> bool:
        """
        Convert MP3 to M4A
        """

        cmd: list[str] = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.input_path),
            "-c:a",
            "aac",
            "-q:a",
            "2",  # Auto quality (VBR)
            "-map_metadata",
            "-1",  # Remove ALL tags (Global)
            "-map_chapters",
            "-1",  # Deletes chapters if present
            "-vn",  # Delete the cover art (Video None)
            "-sn",  # Remove subtitles/lyrics (Subtitle None)
            str(self.output_path),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print("Error conversion MP3 to M4A: %s", e.stderr.decode())

        return False

    def _clean_m4a(self) -> bool:
        """
        Clean M4A/M4B from tags and cover.
        """

        cmd: list[str] = [
            "ffmpeg",
            "-i",
            str(self.input_path),
            "-c",
            "copy",
            "-map_metadata",
            "-1",
            "-map_chapters",
            "-1",
            "-vn",
            "-sn",
            str(self.output_path),
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print("Error clean M4A: %s", e.stderr.decode())

        return False
