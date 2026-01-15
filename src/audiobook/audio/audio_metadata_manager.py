"""Handle media file (MP3, M4B) to get metadata"""

import os
import subprocess
import json
from typing import List
from typing import Optional
from mutagen._util import MutagenError
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from audiobook.audio.handler import MP3Handler, M4BHandler
from audiobook.audio.types import AudioTags, ChapterTag


class AudioMetadataManager:
    """Handle media file (MP3, M4B) to get metadata"""

    def __init__(self, file_path: str):
        self._path = file_path
        self._extension = os.path.splitext(file_path)[1].lower()
        # On instancie le bon handler
        if self._extension == ".mp3":
            self._handler = MP3Handler(file_path)
        elif self._extension == ".m4b":
            self._handler = M4BHandler(file_path)
        else:
            self._handler = None

        self._tags: AudioTags = self._get_empty_metadata()

    def _get_empty_metadata(self) -> AudioTags:
        """Return empty `AudioTags`"""
        return {
            "title": None,
            "subtitle": None,
            "artist": None,
            "album_artist": None,
            "album": None,
            "composer": None,
            "genre": None,
            "year": None,
            "track": None,
            "disc": None,
            "comment": None,
            "description": None,
            "synopsis": None,
            "language": None,
            "copyright": None,
            "publisher": None,
            "series": None,
            "series_part": None,
            "isbn": None,
            "asin": None,
            "compilation": False,
            "chapters": [],
        }

    def extract(self) -> AudioTags:
        """Extract metadata and return as `AudioTags`"""
        data = self._get_empty_metadata()
        if self._handler:
            self._handler.extract(data)
            if self._extension == ".m4b":  # Optionnel : chapitres via FFprobe
                data["chapters"] = self._get_chapters()

        self._tags = data

        return data

    def inject(self, data: AudioTags) -> bool:
        """Take `AudioTags` as parameter and inject it to handled media file"""
        if self._handler:
            self._handler.inject(data)
            return True
        return False

    def clear(self) -> bool:
        """Delete all tags (atoms too) and cover from media file"""
        temp = f"{self._path}.tmp{self._extension}"
        try:
            # 1. FFmpeg : Nettoyage global (metadata et chapitres)
            # On ajoute -vn pour s'assurer que FFmpeg ne traite pas la cover comme un flux vidéo
            cmd = [
                "ffmpeg",
                "-i",
                self._path,
                "-map_metadata",
                "-1",
                "-map_chapters",
                "-1",
                "-vn",  # Supprime les flux "vidéo" (souvent là où se cachent les covers)
                "-c",
                "copy",
                temp,
                "-y",
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            os.replace(temp, self._path)

            # 2. Mutagen : Double vérification pour supprimer les résidus d'image
            if self._extension == ".mp3":
                audio = MP3(self._path, ID3=ID3)
                if audio.tags:  # type: ignore
                    audio.tags.delall("APIC")  # type: ignore
                    audio.save()  # type: ignore
            elif self._extension == ".m4b":
                audio = MP4(self._path)
                if audio.tags and "covr" in audio.tags:
                    del audio.tags["covr"]
                    audio.save()  # type: ignore

            return True

        except MutagenError as e:
            # Erreur spécifique à la lecture/écriture des tags
            print(f"Erreur Mutagen : {e}")
            if os.path.exists(temp):
                os.remove(temp)
        except PermissionError:
            # Le fichier est peut-être ouvert ailleurs (très courant sur Windows)
            print("Erreur : Permission refusée. Le fichier est peut-être utilisé.")
        except FileNotFoundError:
            print(f"Erreur : Le fichier {self._path} n'existe pas.")

        return False

    def _get_chapters(self) -> List[ChapterTag]:
        """Get chapters from M4B"""
        if self._extension == ".mp3":
            return []

        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_chapters",
            self._path,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            raw_data = json.loads(res.stdout)

            # On extrait la liste brute
            chapters_raw = raw_data.get("chapters", [])

            # On construit la liste en forçant le type à chaque étape
            chapters: List[ChapterTag] = []
            for c in chapters_raw:
                chapter: ChapterTag = {
                    "id": int(c.get("id", 0)),
                    "time_base": str(c.get("time_base", "1/1000")),
                    "start": int(c.get("start", 0)),
                    "start_time": float(c.get("start_time", 0.0)),
                    "end": int(c.get("end", 0)),
                    "end_time": float(c.get("end_time", 0.0)),
                    "title": str(c.get("tags", {}).get("title", "")),
                }
                chapters.append(chapter)

            return chapters
        except (
            subprocess.CalledProcessError,
            json.JSONDecodeError,
            KeyError,
            ValueError,
        ):
            # Il est préférable de catcher des erreurs spécifiques que de faire un except nu
            return []

    def extract_cover(self) -> Optional[bytes]:
        """Get cover as bytes from media file"""
        return self._handler.extract_cover() if self._handler else None

    def inject_cover(self, img_data: bytes | None) -> bool:
        """Inject cover from bytes to media file"""
        if not img_data:
            print("No cover!")
            return False
        return self._handler.inject_cover(img_data) if self._handler else False

    def has_cover(self) -> bool:
        """Check if the media file has an embedded cover"""
        if self._handler:
            return self._handler.has_cover()
        return False

    def __str__(self) -> str:
        return (
            f"AudioMetadataManager(\n"
            f"  path:  {self._path}\n"
            f"  extension:  {self._extension}\n"
            # pylint: disable=line-too-long
            f"  tags:  {json.dumps(self._tags, indent=4, ensure_ascii=False)}\n"
            f")"
        )
