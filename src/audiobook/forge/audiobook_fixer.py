import subprocess
from pathlib import Path
from typing import Optional
from mutagen.mp4 import MP4
import audiobook.utils as utils


class AudiobookFixer:
    """
    A utility class to repair and normalize M4B files,
    making them readable by Mutagen and standard audio players.
    """

    def __init__(self, input_path: str):
        self.success = False
        self.final_output: Path | None = None
        self.input_path = Path(input_path).resolve()
        if not self.input_path.exists():
            raise FileNotFoundError(f"File not found: {self.input_path}")

    def replace(self) -> None:
        p = Path(self.input_path)
        utils.rename_file(str(self.final_output), p.stem)

    def fix_structure(self, output_path: Optional[str] = None) -> Path:
        if output_path:
            self.final_output = Path(output_path).resolve()
        else:
            self.final_output = self.input_path.with_name(
                f"{self.input_path.stem}_fixed.m4b"
            )

        print(f"🛠 Repairing structure: {self.input_path.name}...")

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(self.input_path),
            "-map",
            "0:a",
            "-map_chapters",
            "0",
            "-c",
            "copy",
            "-f",
            "mp4",
            "-movflags",
            "+faststart",
            "-metadata",
            f"title={self.input_path.stem}",
            "-loglevel",
            "error",
            str(self.final_output),
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Container rebuilt: {self.final_output.name}")
            return self.final_output
        except subprocess.CalledProcessError:  # Removed 'as e' because it wasn't used
            print("⚠️ Standard repair failed, trying stripped metadata mode...")

            cmd_fallback = [
                "ffmpeg",
                "-y",
                "-i",
                str(self.input_path),
                "-map",
                "0:a",
                "-map_chapters",
                "0",
                "-c",
                "copy",
                "-f",
                "mp4",
                "-map_metadata",
                "-1",
                "-metadata",
                f"title={self.input_path.stem}",
                "-movflags",
                "+faststart",
                "-loglevel",
                "error",
                str(self.final_output),
            ]

            try:
                subprocess.run(cmd_fallback, check=True)
                print(f"✅ Recovery successful: {self.final_output.name}")
                self.success = True
                return self.final_output
            except subprocess.CalledProcessError as err:
                # Here we use 'err' so the linter is happy and you get the details
                print(f"❌ Critical failure: FFmpeg returned code {err.returncode}")
                self.success = False
                raise err

    def verify_with_mutagen(self, file_path: Path) -> bool:
        """
        Checks if the file is now readable by Mutagen's MP4 class.
        """
        try:
            audio = MP4(file_path)
            duration = int(audio.info.length)
            print(f"📋 Mutagen validation: SUCCESS (Duration: {duration}s)")
            self.success = True
            return True
        except Exception as e:
            print(f"⚠️ Mutagen still rejects the file: {e}")
            self.success = False
            return False
