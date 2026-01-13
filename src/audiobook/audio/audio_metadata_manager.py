import os
import subprocess
import json
from .mp3_handler import MP3Handler
from .m4b_handler import M4BHandler
from .metadata_encoder import MetadataEncoder
from mutagen.mp4 import MP4


class AudioMetadataManager:
    def __init__(self, file_path: str):
        self.path = file_path
        self.ext = os.path.splitext(file_path)[1].lower()
        # On instancie le bon handler
        if self.ext == ".mp3":
            self.handler = MP3Handler(file_path)
        elif self.ext == ".m4b":
            self.handler = M4BHandler(file_path)
        else:
            self.handler = None

    def _get_empty_metadata(self):
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

    def extract(self, printing=False):
        data = self._get_empty_metadata()
        if self.handler:
            self.handler.extract(data)
            if self.ext == ".m4b":  # Optionnel : chapitres via FFprobe
                data["chapters"] = self._get_chapters()
        if printing:
            print(json.dumps(data, indent=4, ensure_ascii=False, cls=MetadataEncoder))
        return data

    def inject(self, data):
        if self.handler:
            return self.handler.inject(data)
        return False

    def clear(self) -> bool:
        """Supprime les tags, les chapitres et la pochette (cover)."""
        temp = f"{self.path}.tmp{self.ext}"
        try:
            # 1. FFmpeg : Nettoyage global (metadata et chapitres)
            # On ajoute -vn pour s'assurer que FFmpeg ne traite pas la cover comme un flux vidéo
            cmd = [
                "ffmpeg",
                "-i",
                self.path,
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
            os.replace(temp, self.path)

            # 2. Mutagen : Double vérification pour supprimer les résidus d'image
            if self.ext == ".mp3":
                audio = MP3(self.path, ID3=ID3)
                if audio.tags:
                    audio.tags.delall("APIC")
                    audio.save()
            elif self.ext == ".m4b":
                audio = MP4(self.path)
                if audio.tags and "covr" in audio.tags:
                    del audio.tags["covr"]
                    audio.save()

            return True
        except Exception as e:
            if os.path.exists(temp):
                os.remove(temp)
            print(f"Clear Error: {e}")
            return False

    def _get_chapters(self):
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_chapters",
            self.path,
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            return [
                {
                    "id": c["id"],
                    "time_base": c["time_base"],
                    "start": c["start"],
                    "start_time": float(c["start_time"]),
                    "end": c["end"],
                    "end_time": float(c["end_time"]),
                    "title": c.get("tags", {}).get("title", ""),
                }
                for c in json.loads(res.stdout).get("chapters", [])
            ]
        except:
            return []

    def extract_cover(self) -> Optional[bytes]:
        return self.handler.extract_cover() if self.handler else None

    def inject_cover(self, img_data: bytes) -> bool:
        return self.handler.inject_cover(img_data) if self.handler else False
