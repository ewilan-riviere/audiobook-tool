"""Forge FFmpeg runner"""

import subprocess
from pathlib import Path


class BlacksmithRunner:
    """Blacksmith FFmpeg runner"""

    @staticmethod
    def encode_to_aac(input_path: Path, output_path: Path, bitrate: str) -> str:
        """Encode audio file to AAC"""
        cmd = [
            "ffmpeg",
            "-y",
            "-err_detect",
            "ignore_err",
            "-i",
            str(input_path),
            "-map",
            "0:a:0",  # Uniquement la première piste audio
            "-vn",
            "-sn",
            "-dn",  # Ignore tout ce qui n'est pas audio
            "-c:a",
            "aac",
            "-b:a",
            bitrate,
            "-ar",
            "44100",
            "-ac",
            "2",
            "-map_metadata",
            "-1",  # <--- SUPPRIME TOUTES LES MÉTADONNÉES SOURCES
            "-fflags",
            "+bitexact",  # Force un flux propre
            "-loglevel",
            "error",  # <--- Nettoie ta console des erreurs non fatales
            str(output_path),
        ]
        subprocess.run(cmd, check=True)
        return input_path.name

    @staticmethod
    def merge_to_m4b(input_list: Path, meta_file: Path, output_path: Path) -> Path:
        """Merge M4A to one M4B without metadata warnings"""
        temp_combined = output_path.with_suffix(".temp.m4a")
        working_dir = input_list.parent

        # 1. Concaténation : On ignore TOUT sauf l'audio dès l'entrée
        concat_cmd = [
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
            "-map",
            "0:a",  # Force UNIQUEMENT l'audio (ignore les pistes de chapitres QT)
            "-map_metadata",
            "-1",  # Supprime les métadonnées globales sources
            "-map_chapters",
            "-1",  # Supprime les chapitres sources
            "-bsf:a",
            "aac_adtstoasc",
            "-loglevel",
            "error",
            temp_combined.name,
        ]

        # 2. Ajout des métadonnées propres
        metadata_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            temp_combined.name,
            "-i",
            meta_file.name,
            "-map",
            "0:a",
            "-map_metadata",
            "1",  # On injecte nos nouvelles métadonnées
            "-map_chapters",
            "1",  # On injecte nos nouveaux chapitres
            "-c",
            "copy",
            "-f",
            "mp4",
            "-movflags",
            "+faststart",
            "-loglevel",
            "error",
            output_path.name,
        ]

        try:
            # Étape 1 : Fusion "Brute" (Audio seul)
            subprocess.run(concat_cmd, cwd=working_dir, check=True)

            # Étape 2 : Reconstruction du conteneur M4B final
            subprocess.run(metadata_cmd, cwd=working_dir, check=True)

        finally:
            if temp_combined.exists():
                temp_combined.unlink()

        return output_path
