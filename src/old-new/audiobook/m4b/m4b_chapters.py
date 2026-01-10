import subprocess
import json
from typing import List, Dict, Any
from .m4b_chapter import M4bChapter


class M4bChapters:
    def __init__(self, m4b_file: str) -> None:
        self.m4b_file: str = m4b_file

    def get_chapters(self) -> List[M4bChapter]:
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
            self.m4b_file,
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
