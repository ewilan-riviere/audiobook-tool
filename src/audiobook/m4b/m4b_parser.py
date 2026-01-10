"""Parse M4B to extract chapters and cover"""

import subprocess
import json
import base64
import tempfile
from pathlib import Path
import os
from typing import List, Dict, Any
from .m4b_chapter import M4bChapter, chapter_print


class M4bParser:
    """Parse M4B to extract chapters and cover"""

    def __init__(self, m4b_file: str) -> None:
        self._m4b_file: str = m4b_file
        self._chapters = self.__extract_chapters()
        self._cover_data = self.__extract_raw_cover()
        self._cover_temp_file = self.__save_cover()

    @property
    def path(self) -> str:
        """Get path of M4B file"""
        return self._m4b_file

    @property
    def chapters(self) -> List[M4bChapter]:
        """List chapters as M4bChapter"""
        return self._chapters

    @property
    def cover_base64(self) -> str:
        """Retourne la couverture sous forme de chaîne base64 (lecture seule)."""
        if not self._cover_data:
            return ""
        encoded = base64.b64encode(self._cover_data).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"

    def chapters_print(self) -> None:
        """Print chapters as M4bChapter"""
        for chapter in self._chapters:
            chapter_print(chapter)

    @property
    def cover(self) -> str:
        """Get cover path temp file"""
        return str(self._cover_temp_file)

    def cover_delete(self) -> bool:
        if self._cover_temp_file.exists():
            os.remove(self._cover_temp_file)

        return self._cover_temp_file.exists()

    def __save_cover(self, extension: str = ".jpg") -> Path:
        """
        Décode une image base64 et la sauvegarde dans un fichier temporaire.
        Retourne l'objet Path du fichier créé.
        """
        base64_image = self.cover_base64
        if "," in base64_image:
            base64_image = base64_image.split(",")[1]

        img_data = base64.b64decode(base64_image)

        with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
            temp_file.write(img_data)
            return Path(temp_file.name)

    def __extract_chapters(self) -> List[M4bChapter]:
        """
        Extrait les chapitres du fichier m4b en utilisant ffprobe.
        Retourne une liste de dictionnaires typés M4bChapter.
        """
        cmd: List[str] = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_chapters",
            self._m4b_file,
        ]

        try:
            # On capture la sortie avec check=True pour lever une exception en cas d'erreur
            result: subprocess.CompletedProcess[str] = subprocess.run(
                cmd, capture_output=True, text=True, check=True
            )

            # On parse le JSON
            data: Dict[str, Any] = json.loads(result.stdout)

            # On force le type en List[ChapterDict] pour l'analyseur statique (mypy, etc.)
            chapters: List[M4bChapter] = data.get("chapters", [])
            return chapters

        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            # Retourne une liste vide en cas d'erreur technique
            return []

    def __extract_raw_cover(self) -> bytes:
        """Extrait les octets bruts de la couverture via FFmpeg."""
        cmd = [
            "ffmpeg",
            "-i",
            self._m4b_file,
            "-map",
            "0:v",
            "-map",
            "-0:V",
            "-c",
            "copy",
            "-f",
            "image2pipe",
            "pipe:1",
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, check=True)
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return b""
