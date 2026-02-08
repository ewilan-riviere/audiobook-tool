"""Forge FFmpeg runner"""

import subprocess
from pathlib import Path


class FFmpegRunner:
    """Forge FFmpeg runner"""

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
        # cmd = [
        #     "ffmpeg",
        #     "-y",
        #     "-i",
        #     str(input_path),
        #     "-c:a",
        #     "aac",
        #     "-b:a",
        #     bitrate,
        #     "-ar",
        #     "44100",  # Force la fréquence à 44.1kHz (Standard M4B)
        #     "-ac",
        #     "2",  # Force le passage en Stéréo (2 canaux)
        #     "-loglevel",
        #     "error",
        #     str(output_path),
        # ]
        subprocess.run(cmd, check=True)
        return input_path.name

    @staticmethod
    def merge_to_m4b(input_list: Path, meta_file: Path, output_path: Path) -> None:
        """Merge M4A to one M4B"""
        temp_combined = output_path.with_suffix(".temp.m4a")
        working_dir = input_list.parent

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
            "-bsf:a",
            "aac_adtstoasc",
            "-loglevel",
            "error",
            temp_combined.name,
        ]
        # concat_cmd = [
        #     "ffmpeg",
        #     "-y",
        #     "-f",
        #     "concat",
        #     "-safe",
        #     "0",
        #     "-i",
        #     input_list.name,
        #     "-c",
        #     "copy",
        #     "-bsf:a",
        #     "aac_adtstoasc",  # <--- Syntaxe corrigée ici
        #     "-loglevel",
        #     "error",
        #     temp_combined.name,
        # ]

        metadata_cmd = [
            "ffmpeg",
            "-y",
            "-i",
            temp_combined.name,
            "-i",
            meta_file.name,
            "-map_metadata",
            "1",
            # On force l'utilisation des tags de chapitres du fichier meta
            "-map",
            "0:a",
            "-c",
            "copy",
            "-f",
            "mp4",  # M4B est un conteneur MP4
            "-movflags",
            "+faststart",
            "-loglevel",
            "error",
            output_path.name,
        ]
        # metadata_cmd = [
        #     "ffmpeg",
        #     "-y",
        #     "-i",
        #     temp_combined.name,
        #     "-i",
        #     meta_file.name,
        #     "-map_metadata",
        #     "1",
        #     "-c",
        #     "copy",
        #     "-movflags",
        #     "+faststart",
        #     "-loglevel",
        #     "error",
        #     output_path.name,
        # ]

        try:
            # 1. Concaténation
            subprocess.run(
                concat_cmd,
                cwd=working_dir,
                check=True,
            )

            # 2. Ajout des métadonnées et finalisation en M4B
            subprocess.run(
                metadata_cmd,
                cwd=working_dir,
                check=True,
            )
        finally:
            if temp_combined.exists():
                temp_combined.unlink()
