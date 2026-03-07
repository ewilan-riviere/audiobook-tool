"""Fast fix with remuxing"""

from pathlib import Path
import subprocess


class Remuxer:
    """Fast fix with remuxing"""

    def __init__(self, input_path: Path, output_path: Path) -> None:
        self.input_path = input_path
        self.output_path = output_path

    def run(self) -> bool:
        cmd: list[str] = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(self.input_path),
            "-c",
            "copy",
            "-map_metadata",
            "0",
            "-ignore_unknown",
            str(self.output_path),
        ]

        try:
            print("Attempting FAST fix (remuxing)...")
            subprocess.run(cmd, check=True, capture_output=True)
            return True

        except subprocess.CalledProcessError as e:
            error: str = e.stderr.decode() if e.stderr else "Unknown error"
            print("Fast fix failed. Attempting full re-encoding...")
            print(error)
            if self.output_path.exists():
                self.output_path.unlink()

        return False
