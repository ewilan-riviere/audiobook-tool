"""Handle audio with mutagen"""

from typing import Any, Optional, List
from pathlib import Path
import ffmpeg  # type: ignore
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from .metadata_chapter import MetadataChapter


class MetadataFile:
    """Handle audio file with mutagen"""

    def __init__(self, path: Path | str):
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            print(f"Error: file not exists {path}")
            return

        self.path = path
        self._load()

        if not self.instance:
            print(f"Unable to get instance of {self.path}")
            return

        self.metadata: dict[str, Any] = dict(self.instance)
        self._handle_standard_metadata()
        self._handle_custom_metadata()

        self.chapters = []
        if self.is_m4b:
            self.chapters = self._handle_chapters()

        self.duration = self._handle_duration()

    @property
    def chapters_print(self):
        """Print chapters into console"""
        for chapter in self.chapters:
            print(chapter.string)

    def update_tags(self, tags: dict[str, Any]):
        """Update tags of file"""
        mp4 = self.mp4

        # 1. Mappage des tags standards
        mapping = {
            "title": "\xa9nam",
            "album": "\xa9alb",
            "artist": "\xa9ART",
            "album_artist": "aART",
            "composer": "\xa9wrt",
            "genre": "\xa9gen",
            "date": "\xa9day",
            "copyright": "cprt",
            "comment": "\xa9cmt",
            "description": "desc",
            "synopsis": "ldes",
            "compilation": "cpil",
        }

        for key, atom in mapping.items():
            if key in tags:
                if tags[key]:
                    value = str(tags[key])
                    mp4[atom] = [value]

        # 2. Gestion spécifique de la piste (Tuple: (piste_actuelle, total))
        if "track" in tags:
            mp4["trkn"] = [(int(tags["track"]), 0)]
        if "disc" in tags:
            mp4["disk"] = [(int(tags["disc"]), 0)]

        mp4.save()  # type: ignore

    def update_tags_custom(self, tags: dict[str, Any]):
        """Update tags custom of file"""
        mp4 = self.mp4
        # 3. Tags personnalisés (Freeform atoms)
        custom_tags = {
            "lyrics": "----:com.apple.iTunes:lyrics",
            "publisher": "----:com.apple.iTunes:publisher",
            "language": "----:com.apple.iTunes:language",
            "series": "----:com.apple.iTunes:series",
            "series-part": "----:com.apple.iTunes:series-part",
            "subtitle": "----:com.apple.iTunes:subtitle",
            "isbn": "----:com.apple.iTunes:ISBN",
            "asin": "----:com.apple.iTunes:ASIN",
        }

        for key, atom in custom_tags.items():
            if key in tags:
                # Pour les atomes '----', Mutagen attend souvent des bytes
                if tags[key]:
                    value = str(tags[key])
                    mp4[atom] = [value.encode("utf-8")]

    def update_cover(self, cover_path: str):
        """
        Ajoute ou remplace la pochette du fichier M4B.
        Supporte JPEG et PNG.
        """
        mp4 = self.mp4

        with open(cover_path, "rb") as f:
            data = f.read()

        # Déterminer le format de l'image
        if cover_path.lower().endswith((".jpg", ".jpeg")):
            kind = MP4Cover.FORMAT_JPEG
        elif cover_path.lower().endswith(".png"):
            kind = MP4Cover.FORMAT_PNG
        else:
            print("Format d'image non supporté (utilisez JPG ou PNG)")
            return

        # Créer l'objet cover et l'assigner à l'atome 'covr'
        # Note: 'covr' est une liste car un MP4 peut techniquement avoir plusieurs images
        mp4["covr"] = [MP4Cover(data, imageformat=kind)]

        mp4.save()  # type:ignore

    def remove_cover(self):
        """Remove cover from media file"""
        if self.is_mp3:
            # Supprime toutes les frames d'images (APIC)
            self.id3.delall("APIC")  # type: ignore
            self.id3.save()  # type: ignore
        elif self.is_m4b:
            if "covr" in self.mp4.tags:  # type: ignore
                del self.mp4.tags["covr"]  # type: ignore
                self.mp4.save()  # type: ignore
            else:
                print(f"Error: no cover found for {self.path}")

    def _load(self):
        """Load audio from mutagen"""
        self.is_mp3 = False
        self.is_m4b = False

        p = Path(self.path)
        self.basename = p.name
        self.filename = p.stem

        if str(self.path).endswith(".mp3"):
            self.instance = EasyID3(self.path)
            self.id3 = ID3(self.path)
            self.is_mp3 = True
            self.extension = "MP3"
        elif str(self.path).endswith(".m4b") or str(self.path).endswith(".m4a"):
            self.instance = EasyMP4(self.path)
            self.mp4 = MP4(self.path)
            self.is_m4b = True
            self.extension = "M4B"

    def _handle_standard_metadata(self):
        self.album = self._extract_meta("album")
        is_compilation = self._extract_meta("compilation")
        self.composer = self._extract_meta("composer")
        self.copyright = self._extract_meta("version")
        self.title = self._extract_meta("title")
        self.subtitle = self._extract_meta("version")
        self.artist = self._extract_meta("artist")
        self.album_artist = self._extract_meta("albumartist")
        self.disc_number = self._extract_meta("discnumber")
        self.publisher = self._extract_meta("organization")
        track = self._extract_meta("tracknumber")
        self.language = self._extract_meta("language")
        self.genre = self._extract_meta("genre")
        year = self._extract_meta("date")
        self.asin = self._extract_meta("asin")

        if is_compilation and is_compilation == "1":
            self.is_compilation = True
        else:
            self.is_compilation = False
        if year:
            self.year = int(year)
        else:
            self.year = None
        if track:
            if "/" in track:
                track = track.split("/")
                track = track[0]
            self.track = int(track)
        else:
            self.track = None

    def _handle_custom_metadata(self):
        if self.is_mp3:
            self.comment = self._extract_meta_id3("COMM::eng")
            if not self.comment:
                self.comment = self._extract_meta_id3("COMM:ID3v1 Comment:eng")

            self.encoder = self._extract_meta_id3("TSSE")
            self.synopsis = self._extract_meta_id3("TDES")
            self.compatible_brands = self._extract_meta_id3("TXXX:compatible_brands")
            self.major_brand = self._extract_meta_id3("TXXX:major_brand")
            self.minor_version = self._extract_meta_id3("TXXX:minor_version")
            self.description = self._extract_meta_id3("TXXX:DESCRIPTION")
            self.series = self._extract_meta_id3("TXXX:SERIES")
            self.series_part = self._extract_meta_id3("TXXX:SERIES-PART")
            self.lyrics = self._extract_meta_id3("TXXX:LYRICS")
            self.isbn = self._extract_meta_id3("TXXX:ISBN")
        elif self.is_m4b:
            self.encoder = self._extract_meta_mp4("©too")
            self.subtitle = self._extract_meta_mp4("----:com.apple.iTunes:SUBTITLE")
            self.series_part = self._extract_meta_mp4(
                "----:com.apple.iTunes:SERIES-PART"
            )
            self.series = self._extract_meta_mp4("----:com.apple.iTunes:SERIES")
            self.publisher = self._extract_meta_mp4("©pub")
            self.synopsis = self._extract_meta_mp4("ldes")
            self.lyrics = self._extract_meta_mp4("©lyr")
            self.language = self._extract_meta_mp4("----:com.apple.iTunes:LANGUAGE")
            self.isbn = self._extract_meta_mp4("----:com.apple.iTunes:ISBN")
            self.description = self._extract_meta_mp4("desc")
            self.copyright = self._extract_meta_mp4("cprt")
            self.composer = self._extract_meta_mp4("©wrt")
            self.comment = self._extract_meta_mp4("©cmt")
            self.asin = self._extract_meta_mp4("----:com.apple.iTunes:ASIN")

    def _handle_chapters(self) -> List[MetadataChapter]:
        """Parse chapters into M4B file"""
        probe = ffmpeg.probe(self.path, show_chapters=None)  # type: ignore

        chapters: List[MetadataChapter] = []
        chaps = probe.get("chapters", [])
        for chap in chaps:
            chapter = MetadataChapter(chap)
            chapters.append(chapter)

        return chapters

    def _handle_duration(self):
        if self.is_mp3:
            audio = MP3(self.path)
            return int(audio.info.length)
        elif self.is_m4b:
            return int(self.mp4.info.length)
        else:
            return 0

    def _extract_meta(self, key: str) -> str | None:
        if key in self.metadata:
            return self.metadata[key][0]

        return None

    def _extract_meta_id3(self, key: str) -> Optional[str]:
        frame = self.id3.get(key)  # type: ignore
        if frame:
            if hasattr(frame, "text") and frame.text:  # type: ignore
                return frame.text[0]  # type: ignore
            return str(frame)  # type: ignore

        return None

    def _extract_meta_mp4(self, key: str) -> Optional[str]:
        # self.tags correspond ici à votre objet MP4Tags
        frame = self.mp4.get(key)  # type: ignore

        if frame:
            # Les tags MP4 sont presque toujours des listes
            if isinstance(frame, list) and len(frame) > 0:  # type: ignore
                first_item = frame[0]  # type: ignore

                # Cas des tags 'Freeform' (votre cas avec '----:com.apple.iTunes...')
                if hasattr(first_item, "value"):  # type: ignore
                    val = first_item.value  # type: ignore
                    # pylint: disable=line-too-long
                    return val.decode("utf-8") if isinstance(val, bytes) else str(val)  # type: ignore

                # Cas des tags standards (ex: '©nam', '©art') qui sont des strings ou bytes
                return (
                    first_item.decode("utf-8")
                    if isinstance(first_item, bytes)
                    else str(first_item)  # type: ignore
                )

            # Si ce n'est pas une liste (rare en MP4 mutagen)
            return str(frame)  # type: ignore

        return None

    def __str__(self) -> str:
        return (
            f"MetadataFile(\n"
            f"  path:   {getattr(self, 'path', None)}\n"
            f"  basename:   {getattr(self, 'basename', None)}\n"
            f"  filename:   {getattr(self, 'filename', None)}\n"
            f"  extension:   {getattr(self, 'extension', None)}\n"
            f"  album:   {getattr(self, 'album', None)}\n"
            f"  album_artist:   {getattr(self, 'album_artist', None)}\n"
            f"  artist:   {getattr(self, 'artist', None)}\n"
            f"  asin:   {getattr(self, 'asin', None)}\n"
            f"  comment:   {getattr(self, 'comment', None)}\n"
            f"  compatible_brands:   {getattr(self, 'compatible_brands', None)}\n"
            f"  composer:   {getattr(self, 'composer', None)}\n"
            f"  copyright:   {getattr(self, 'copyright', None)}\n"
            f"  description:   {getattr(self, 'description', None)}\n"
            f"  disc_number:   {getattr(self, 'disc_number', None)}\n"
            f"  encoder:   {getattr(self, 'encoder', None)}\n"
            f"  genre:   {getattr(self, 'genre', None)}\n"
            f"  is_compilation:   {getattr(self, 'is_compilation', None)}\n"
            f"  isbn:   {getattr(self, 'isbn', None)}\n"
            f"  language:   {getattr(self, 'language', None)}\n"
            f"  lyrics:   {getattr(self, 'lyrics', None)}\n"
            f"  major_brand:   {getattr(self, 'major_brand', None)}\n"
            f"  minor_version:   {getattr(self, 'minor_version', None)}\n"
            f"  publisher:   {getattr(self, 'publisher', None)}\n"
            f"  series:   {getattr(self, 'series', None)}\n"
            f"  series_part:   {getattr(self, 'series_part', None)}\n"
            f"  subtitle:   {getattr(self, 'subtitle', None)}\n"
            f"  synopsis:   {getattr(self, 'synopsis', None)}\n"
            f"  title:   {getattr(self, 'title', None)}\n"
            f"  track:   {getattr(self, 'track', None)}\n"
            f"  year:   {getattr(self, 'year', None)}\n"
            f"  chapters:   {len(self.chapters)}\n"
            f")"
        )
