"""Handle config for build audiobook-tool"""

import re
import tempfile
from pathlib import Path
import unicodedata
from audiobook.audio.reader.main import AudioReader
from audiobook.models.m4b import M4bAudiobook
import audiobook.utils as utils
from audiobook.args import AudiobookArgs
from audiobook.yml import YmlReader
from audiobook.audio import AudioWriter
from audiobook.env import PART_SIZE
from audiobook.common import AutoRepr


class ConfigBuild(AutoRepr):
    """Handle config for build audiobook-tool"""

    def __init__(self, args: AudiobookArgs):
        # /path/to/the-wall (with .mp3, metadata.yml, cover.jpg)
        source_path = self._to_path(args.source_directory)
        if not source_path:
            raise FileNotFoundError(f"Path {source_path} is not valid!")
        self.source_path = source_path
        # Structured
        self.structured = args.structured

        # Setup temporary directory (for clean work)
        # /var/folders/m0/xhm5c_mx7yn2b8mqtqhdpc840000gn/T/tmppa8g2g_n
        self.temporary_directory = tempfile.TemporaryDirectory()

        # Load metadata.yml and get tags
        # /path/to/the-wall/metadata.yml
        self.yml_path = utils.get_file(self.source_path, "yml")
        reader: YmlReader | None = None
        if self.yml_path:
            reader = YmlReader(self.yml_path).read()
            # M4bAudiobook for tags from metadata.yml to write inside future M4B
            self.audiobook = reader.to_audiobook()
        else:
            self.audiobook = M4bAudiobook()
            files = utils.get_files(source_path, "mp3")
            if not files:
                files = utils.get_files(source_path, "m4a")
            if files:
                first_file = files[0]
                self.audiobook.from_reader_tags(AudioReader(first_file).tags)

        # Load cover
        # /path/to/the-wall/cover.jpg
        self.cover_path = utils.get_file(self.source_path, "jpg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.source_path, "jpeg")
        if not self.cover_path:
            self.cover_path = utils.get_file(self.source_path, "png")

        # /path/to/the-wall/Assassin’s Apprentice
        self.output_path = self._handle_output_path(args, reader)

        # Single or unified
        self.unified = args.unified
        # Part of each size (if not single)
        if args.part_size:
            self.part_size = int(args.part_size)
        else:
            self.part_size = int(PART_SIZE)

    @property
    def working_path(self) -> Path:
        """Get `temporary_directory` as `Path`"""
        return Path(self.temporary_directory.name)

    def _handle_output_path(
        self,
        args: AudiobookArgs,
        reader: YmlReader | None,
    ) -> Path:
        """Set M4B output path, based on metadata"""
        default_title = "Unknown"
        custom_output_path = self._to_path(args.output_path)
        output_path: Path | None = custom_output_path

        if custom_output_path:
            output_path = custom_output_path
        else:
            container_name = self.audiobook.title if self.audiobook else default_title
            output_path = self.source_path / utils.safe_filename(container_name)

        output_path = utils.safe_path(output_path)

        if self.structured:
            output_path = self._handle_structured(output_path, default_title, reader)

        output_path_str = re.sub(r"\.{2,}", ".", str(output_path))

        return Path(output_path_str).resolve()

    def _handle_structured(
        self, output_path: Path, default_title: str, reader: YmlReader | None
    ) -> Path:
        if not reader or not reader.metadata:
            return output_path

        authors = reader.metadata.authors
        if not authors:
            return output_path
        splitted_authors = [a.strip() for a in authors.split("&")]
        if not splitted_authors or len(splitted_authors) == 0:
            return output_path
        first_author = splitted_authors[0]

        title = reader.metadata.title or default_title
        series = reader.metadata.series
        volume = reader.metadata.volume
        suffix_path_str: str = ""
        if series and volume:
            if volume.is_integer():
                volume = int(volume)
            volume = str(volume)
            suffix_path_str = f"{first_author}/{series}/{series}.{volume}.{title}"
        else:
            suffix_path_str = f"{first_author}/{title}"

        suffix_path = self._normalized(suffix_path_str)

        return output_path / suffix_path

    def _normalized(self, text: str | Path) -> Path:
        # Clean conversion to string and normalization of separators
        original_str = str(text).replace("\\", "/")

        # Detect whether the original path was absolute (begins with /)
        is_absolute = original_str.startswith("/")

        parts = original_str.split("/")
        slugified_parts: list[str] = []

        for part in parts:
            if not part:  # Empty segments are ignored (e.g., double //).
                continue

            # Removal of accents
            nfkd_form = unicodedata.normalize("NFKD", part)
            part = "".join([c for c in nfkd_form if not unicodedata.combining(c)])

            # Replacing special characters
            part = re.sub(r"[^a-zA-Z0-9]+", ".", part)
            part = part.strip(".")

            if part:
                slugified_parts.append(part)

        new_path_str = "/".join(slugified_parts)

        if is_absolute:
            new_path_str = "/" + new_path_str

        return Path(new_path_str)

    def remove_working_path(self):
        """Delete `temporary_directory`"""
        self.temporary_directory.cleanup()

    def remove_covers(self):
        """Remove covers from MP3 files"""
        mp3_files = utils.get_files(self.source_path, "mp3")
        items: list[AudioWriter] = []
        for mp3_file in mp3_files:
            items.append(AudioWriter(mp3_file))

        for item in items:
            item.remove_cover()

    def _to_path(self, path: str | Path | None) -> Path | None:
        if not path:
            return None

        return Path(path)
