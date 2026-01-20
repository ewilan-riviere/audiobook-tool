import subprocess
from pathlib import Path


class FFmpegRunner:
    """Interface pour l'exécution des commandes système FFmpeg."""

    @staticmethod
    def encode_to_aac(input_path: Path, output_path: Path, bitrate: str) -> str:
        """Ré-encode un fichier avec paramètres fixes pour garantir la fusion."""
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-c:a",
            "aac",
            "-b:a",
            bitrate,
            "-ar",
            "44100",  # Force la fréquence à 44.1kHz (Standard M4B)
            "-ac",
            "2",  # Force le passage en Stéréo (2 canaux)
            "-loglevel",
            "error",
            str(output_path),
        ]
        subprocess.run(cmd, check=True)
        return input_path.name

    @staticmethod
    def merge_to_m4b(input_list: Path, meta_file: Path, output_path: Path) -> None:
        temp_combined = output_path.with_suffix(".temp.m4a")
        working_dir = input_list.parent

        try:
            # 1. Concaténation avec le bon flag de filtre bitstream
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-f",
                    "concat",
                    "-safe",
                    "0",
                    "-i",
                    input_list.name,
                    "-c",
                    "copy",
                    "-bsf:a",
                    "aac_adtstoasc",  # <--- Syntaxe corrigée ici
                    "-loglevel",
                    "error",
                    temp_combined.name,
                ],
                cwd=working_dir,
                check=True,
            )

            # 2. Ajout des métadonnées
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
