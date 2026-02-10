from pathlib import Path
from typing import Union, Dict, Any, List, cast
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4FreeForm
from mutagen.id3 import Frames, TXXX, COMM, APIC  # type: ignore
from mutagen.mp4 import MP4Cover
from audiobook.common import TAGS_MAPPING, AudioChapter
from audiobook.audio.reader.mutagen import MutagenReader
from .chapter import ChapterWriter


class MutagenWriter:
    """Écrit des tags dans un fichier audio via mutagen"""

    def __init__(self, file_path: Union[str, Path]):
        self.path = Path(file_path)
        self.tags_map = TAGS_MAPPING
        data = mutagen.File(str(self.path))  # type: ignore

        if data is None:
            raise ValueError(f"Impossible d'ouvrir le fichier : {self.path}")

        if isinstance(data, MP3) and data.tags is None:  # type: ignore
            data.add_tags()  # type: ignore

        self.audio = cast(Union[MP3, MP4], data)

    def set_tags(self, tags_to_write: Dict[str, Any]) -> None:
        """Écrit un dictionnaire de tags et sauvegarde le fichier."""
        for human_key, value in tags_to_write.items():
            if human_key in self.tags_map:
                if value is not None:
                    self._set_tag(human_key, value)

        self.save_audio()

    def set_tag(self, tag: str, value: Any) -> None:
        """Write a tag on audio file"""
        self._set_tag(tag, value)
        self.save_audio()

    def _set_tag(self, human_key: str, value: Any) -> None:
        """Définit la valeur d'un tag spécifique."""
        target_dict = self.tags_map.get(human_key)
        if not target_dict:
            return

        if isinstance(self.audio, MP3):
            self._write_mp3_tag(target_dict["mp3"], value)
        elif isinstance(self.audio, MP4):  # type: ignore
            self._write_mp4_tag(target_dict["m4b"], value)

    def set_chapters(self, chapters: List[AudioChapter]):
        """Set chapters on M4B"""
        if not isinstance(self.audio, MP4):
            return

        reader = MutagenReader(self.path)

        chapter = ChapterWriter(self.path)
        chapter.write_chapters(chapters)

        self.set_tags(reader.get_all())

    def _write_mp3_tag(self, key_or_list: Union[str, List[str]], value: Any) -> None:
        """Gestion des frames ID3 pour MP3"""
        # Utilise la première clé si c'est une liste
        key = key_or_list[0] if isinstance(key_or_list, list) else key_or_list
        str_val = str(value)

        # 1. Gestion des TXXX (User Defined Text)
        if key.startswith("TXXX:"):
            desc = key.replace("TXXX:", "")
            self.audio.tags.add(TXXX(encoding=3, desc=desc, text=[str_val]))  # type: ignore

        # 2. Gestion des COMM (Comments)
        elif key.startswith("COMM"):
            parts = key.split(":")
            lang = parts[2] if len(parts) > 2 else "eng"
            desc = parts[1] if len(parts) > 1 else ""
            self.audio.tags.add(  # type: ignore
                COMM(encoding=3, lang=lang, desc=desc, text=[str_val]),
            )

        # 3. Gestion dynamique des autres frames via mutagen.id3.Frames
        else:
            # Frames est un dict contenant TIT2, TIT3, TPE1, etc.
            frame_class = Frames.get(key)  # type: ignore
            if frame_class:
                self.audio.tags.add(frame_class(encoding=3, text=[str_val]))  # type: ignore
            else:
                # Si la frame n'est pas standard, on bascule en TXXX par sécurité
                self.audio.tags.add(TXXX(encoding=3, desc=key, text=[str_val]))  # type: ignore

    def _write_mp4_tag(self, key_or_list: Union[str, List[str]], value: Any) -> None:
        """Gestion des atoms MP4/M4B"""
        key = key_or_list[0] if isinstance(key_or_list, list) else key_or_list

        # Gestion spécifique trkn/disk (tuples)
        if key in ["trkn", "disk"]:
            self._handle_mp4_numeric_tuple(key, value)
            return

        # Gestion des atoms iTunes personnalisés (FreeForm)
        if key.startswith("----"):
            self.audio[key] = [MP4FreeForm(str(value).encode("utf-8"))]

        # Gestion booléens
        elif key == "cpil":
            self.audio[key] = [bool(value)]

        else:
            self.audio[key] = [str(value)]

    def _handle_mp4_numeric_tuple(self, key: str, value: Any) -> None:
        """Helper pour transformer '1/10' ou (1, 10) en format MP4 [(1, 10)]"""
        if isinstance(value, (list, tuple)):
            self.audio[key] = [value]
        elif isinstance(value, str) and "/" in value:
            parts = [int(p) for p in value.split("/")]
            self.audio[key] = [(parts[0], parts[1] if len(parts) > 1 else 0)]
        else:
            try:
                self.audio[key] = [(int(value), 0)]
            except (ValueError, TypeError):
                pass

    def save_audio(self):
        """Write audio tags"""
        self.audio.save()  # type: ignore

    def set_cover(self, image_path: Union[str, Path]) -> None:
        """Ajoute ou remplace la couverture de l'album."""
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image introuvable : {img_path}")

        mime = (
            "image/jpeg"
            if img_path.suffix.lower() in [".jpg", ".jpeg"]
            else "image/png"
        )
        with open(img_path, "rb") as f:
            img_data = f.read()

        if isinstance(self.audio, MP3):
            # Supprime d'abord les anciennes pochettes (Type 3 = Front Cover)
            self.audio.tags.delall("APIC")  # type: ignore
            self.audio.tags.add(  # type: ignore
                APIC(
                    encoding=3,  # UTF-8
                    mime=mime,  # image/jpeg ou image/png
                    type=3,  # 3 est pour la couverture de face (front cover)
                    desc="Front cover",
                    data=img_data,
                )
            )
        elif isinstance(self.audio, MP4):  # type: ignore
            # Le format MP4 utilise l'atom 'covr'
            # imageformat 13 = JPEG, 14 = PNG
            fmt = MP4Cover.FORMAT_JPEG if mime == "image/jpeg" else MP4Cover.FORMAT_PNG
            self.audio["covr"] = [MP4Cover(img_data, imageformat=fmt)]

        self.save_audio()

    def remove_cover(self) -> None:
        """Supprime toutes les couvertures du fichier."""
        if isinstance(self.audio, MP3):
            self.audio.tags.delall("APIC")  # type: ignore
        elif isinstance(self.audio, MP4):  # type: ignore
            if "covr" in self.audio:
                del self.audio["covr"]

        self.save_audio()

    def remove_tag(self, human_key: str) -> None:
        """Supprime un tag du fichier."""
        target_dict = self.tags_map.get(human_key)
        if not target_dict:
            return

        raw_keys = (
            target_dict["mp3"] if isinstance(self.audio, MP3) else target_dict["m4b"]
        )
        keys = [raw_keys] if isinstance(raw_keys, str) else raw_keys

        for k in keys:
            if isinstance(self.audio, MP3) and self.audio.tags:  # type: ignore
                self.audio.tags.delall(k)  # type: ignore
            elif k in self.audio:
                del self.audio[k]

        self.save_audio()
