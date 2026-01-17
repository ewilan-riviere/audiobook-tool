import subprocess
from pathlib import Path


class FFmpegRunner:
    """Interface pour l'exécution des commandes système FFmpeg."""

    @staticmethod
    def encode_to_aac(input_path: Path, output_path: Path, bitrate: str) -> None:
        """Ré-encode un fichier MP3 unique vers le format AAC (conteneur M4A)."""
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

    @staticmethod
    def merge_to_m4b(input_list: Path, meta_file: Path, output_path: Path) -> None:
        """Combine les fichiers AAC et injecte les chapitres dans le M4B final."""
        temp_combined = output_path.with_suffix(".temp.m4a")
        try:
            # 1. Concaténation des flux AAC
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

            # 2. Injection des métadonnées (Chapitres) et optimisation Faststart
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
