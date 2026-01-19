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
        # Work in the directory of the files to simplify paths for FFmpeg
        working_dir = input_list.parent

        try:
            # 1. Concat with safe 0 and local paths
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    input_list.name,  # Use just the filename
                    "-c",
                    "copy",
                    "-loglevel",
                    "error",
                    temp_combined.name,
                ],
                cwd=working_dir,  # Execute inside the folder
                check=True,
            )

            # 2. Add metadata
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    temp_combined.name,
                    "-i",
                    meta_file.name,
                    "-map_metadata",
                    "1",
                    "-c",
                    "copy",
                    "-movflags",
                    "+faststart",
                    "-loglevel",
                    "error",
                    output_path.name,
                ],
                cwd=working_dir,
                check=True,
            )
        finally:
            if temp_combined.exists():
                temp_combined.unlink()
