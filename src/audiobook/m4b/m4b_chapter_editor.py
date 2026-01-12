"""Edit chapters of M4B file"""

import os
import tempfile
import shutil
import ffmpeg  # type: ignore
import subprocess
from typing import Any
from audiobook.config import AudiobookConfig
from audiobook.metadata import MetadataFile


class M4bChapterEditor:
    """Edit chapters of M4B file"""

    def __init__(self, config: AudiobookConfig):
        self._config = config
        self._m4b_path = str(config.m4b_forge_path)
        if not self._m4b_path:
            print("Error: no m4b_forge_path")

        self._file = MetadataFile(str(self._m4b_path))

    def run(self):
        """Edit chapters of M4B file"""
        try:
            probe = ffmpeg.probe(self._m4b_path, show_chapters=None)  # type: ignore
        except ffmpeg.Error as e:
            print(f"Error ffmpeg with {self._m4b_path}: {e.stderr.decode()}")  # type: ignore
            return

        chapters = probe.get("chapters", [])
        format_tags = probe.get("format", {}).get("tags", {})

        if not chapters:
            print(f"No chapters into {self._m4b_path}")
            return

        metadata_content = ";FFMETADATA1\n"
        for key, value in format_tags.items():
            metadata_content += f"{key}={value}\n"

        for i, ch in enumerate(chapters):
            metadata_content = self._handle_chapter(i, ch, metadata_content)

        self._execute_ffmpeg(metadata_content)

    def _handle_chapter(self, i: int, ch: Any, metadata_content: str):
        # On récupère les temps en secondes (float) pour éviter les overflows d'entiers
        # On utilise float() car start_time est une string dans le JSON de ffprobe
        try:
            start_seconds = float(ch.get("start_time", 0))
            end_seconds = float(ch.get("end_time", 0))
        except (ValueError, TypeError):
            start_seconds = 0
            end_seconds = 0

        # Conversion vers la TIMEBASE 1/1000 (millisecondes)
        start_ms = int(start_seconds * 1000)
        end_ms = int(end_seconds * 1000)

        # Sécurité : Si FFmpeg renvoie des valeurs aberrantes (négatives)
        if start_ms < 0:
            start_ms = 0
        if end_ms < 0:
            end_ms = 0

        # Récupération du titre
        old_title = ch.get("tags", {}).get("title")
        new_title = old_title

        for file in self._config.mp3_metadata:
            if file.filename == old_title:
                new_title = file.title

        metadata_content += "\n[CHAPTER]\n"
        metadata_content += "TIMEBASE=1/1000\n"
        metadata_content += f"START={start_ms}\n"
        metadata_content += f"END={end_ms}\n"
        metadata_content += f"title={new_title}\n"

        return metadata_content

    def _execute_ffmpeg(self, metadata_content: str):
        if not self._m4b_path:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            meta_txt_path = os.path.join(tmpdir, "metadata.txt")
            temp_m4b_path = os.path.join(tmpdir, "temp_output.m4b")

            # Écrire le fichier de métadonnées
            with open(meta_txt_path, "w", encoding="utf-8") as f:
                f.write(metadata_content)

            cmd = [
                "ffmpeg",
                "-i",
                self._m4b_path,
                "-i",
                meta_txt_path,
                "-map",
                "0:a",  # Audio
                "-map",
                "0:v?",  # Cover
                "-map_metadata",
                "1",
                "-map_chapters",
                "1",
                "-c",
                "copy",
                "-disposition:v:0",
                "attached_pic",
                temp_m4b_path,
                "-y",
            ]

            # On ne met PAS text=True ici pour éviter que Python tente de décoder
            # automatiquement avec le mauvais codec.
            try:
                # On ajoute check=True pour lever une exception en cas d'erreur
                subprocess.run(cmd, capture_output=True, check=True)

                # 4. Si succès, on remplace le fichier original
                shutil.move(temp_m4b_path, self._m4b_path)
                print(f"Succès ! {self._m4b_path} mis à jour.")

            except subprocess.CalledProcessError as e:
                # e.stderr contient les logs d'erreur de FFmpeg
                error_msg = e.stderr.decode("utf-8", errors="ignore")
                print(f"Échec de FFmpeg (Code {e.returncode}) :\n{error_msg}")
                print("Le fichier original n'a pas été modifié.")
            except Exception as e:
                print(f"Erreur inattendue : {e}")
                print("Le fichier original n'a pas été modifié.")
