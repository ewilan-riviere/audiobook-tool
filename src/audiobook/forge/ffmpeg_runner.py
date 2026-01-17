import subprocess
from pathlib import Path


class FFmpegRunner:
    """Interface pour l'exécution des commandes système FFmpeg."""

    @staticmethod
    def encode_to_aac(input_path: Path, output_path: Path, bitrate: str) -> str:
        """Ré-encode un fichier et retourne son nom pour le logging."""
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-c:a",
            "aac",
            "-b:a",
            bitrate,
            "-ac",
            "2",
            "-loglevel",
            "error",
            str(output_path),
        ]
        subprocess.run(cmd, check=True)
        return input_path.name

    @staticmethod
    def merge_to_m4b(input_list: Path, meta_file: Path, output_path: Path) -> None:
        temp_combined = output_path.with_suffix(".temp.m4a")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    str(input_list),
                    "-c",
                    "copy",
                    "-loglevel",
                    "error",
                    str(temp_combined),
                ],
                check=True,
            )

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(temp_combined),
                    "-i",
                    str(meta_file),
                    "-map_metadata",
                    "1",
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    "-loglevel",
                    "error",
                    str(output_path),
                ],
                check=True,
            )
        finally:
            if temp_combined.exists():
                temp_combined.unlink()
