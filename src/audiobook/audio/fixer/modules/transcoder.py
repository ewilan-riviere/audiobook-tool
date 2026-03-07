from pathlib import Path
import subprocess


class Transcoder:
    def __init__(self, input_path: Path, output_path: Path) -> None:
        self.input_path = input_path
        self.output_path = output_path
        print(self.input_path)

    def run(self) -> bool:
        cmd: list[str] = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-analyzeduration",
            "20M",
            "-probesize",
            "20M",
            "-i",
            str(self.input_path),
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
            str(self.output_path),
        ]

        try:
            print("Attempting heavy fix (transcoding)...")
            subprocess.run(cmd, check=True, capture_output=True)
            return True

        except subprocess.CalledProcessError as e:
            print(
                "Repair failed: %s", e.stderr.decode() if e.stderr else "Unknown error"
            )
            if self.output_path.exists():
                self.output_path.unlink()

        return False
