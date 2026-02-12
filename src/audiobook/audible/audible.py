"""Fetch metadata from Audible from audiobook ASIN"""

import re
from pathlib import Path
from audiobook.common import AutoRepr
from audiobook.models import AudibleAudiobook
from audiobook.yml import YmlWriter
from .parser import ParserJson, ParserHtml
from .types import JsonAudiobook
from .fetch import AudibleFetch


class Audible(AutoRepr):
    """Fetch metadata from Audible from audiobook ASIN"""

    success: bool = False

    def __init__(self, asin: str, locale: str | None = None):
        self.fetch = AudibleFetch(asin, locale)
        self.audiobook = AudibleAudiobook(asin)

        if not self.fetch.success:
            return

        if not self.fetch.soup or not self.fetch.url:
            return

        self.audiobook.url = self.fetch.url
        web = ParserHtml(self.fetch.soup)
        json = ParserJson(self.fetch.soup)
        self._handle_audiobook(web, json)
        self.success = True

    def save_metadata(self, save_path: str | Path) -> str:
        """Save audiobook as metadata.yml"""
        save_path = Path(save_path).resolve()
        writer = YmlWriter(self.audiobook, save_path)
        writer.write()

        return str(writer.save_path)

    def _handle_audiobook(self, web: ParserHtml, json: ParserJson):
        self.audiobook.original_title = web.html.get("title")
        self.audiobook.subtitle = web.html.get("subtitle")
        self.audiobook.description = web.html.get("description")
        self.audiobook.copyright = web.html.get("copyright")
        self.audiobook.publisher = json.ld_audiobook.get("publisher")

        self.audiobook.authors = self._handle_authors(json.audiobook)
        self.audiobook.narrators = json.audiobook.get("narrators")

        self.audiobook.published_at = json.ld_audiobook.get("date_published")
        self.audiobook.duration = json.ld_audiobook.get("duration")
        language = json.ld_audiobook.get("in_language")
        if language:
            self.audiobook.language = language.capitalize()
        self.audiobook.abridged = json.ld_audiobook.get("abridged")
        self.audiobook.cover = json.ld_audiobook.get("image")

        self.audiobook.volume = None
        self.audiobook.part = None
        self.audiobook.title = None
        self.audiobook.series = None
        self._handle_series(json.audiobook)

        self.audiobook.format = json.audiobook.get("format")
        self.audiobook.book_format = json.ld_audiobook.get("book_format")
        self.audiobook.sku = json.ld_product["sku"]

        self.audiobook.rating = json.audiobook.get("rating")
        self.audiobook.price = json.ld_audiobook.get("price")

        self.audiobook.genres = web.html.get("genres")
        self.audiobook.categories = json.audiobook.get("categories")

        self.audiobook.clean()

    def _handle_authors(self, audio: JsonAudiobook) -> list[str] | None:
        items: list[str] = []
        authors = audio.get("authors")
        if not authors:
            return None

        for author in authors:
            if any(word in author for word in ["traducteur", "translator"]):
                continue
            else:
                items.append(author)

        return items

    def _handle_series(self, audio: JsonAudiobook):
        self.audiobook.original_series = audio.get("series")
        if self.audiobook.series:
            self.audiobook.series = self.audiobook.series[0]
            self.audiobook.part = audio.get("part")

            if self.audiobook.part:
                match = re.search(r"\d+", self.audiobook.part)
                if match:
                    number = int(match.group())
                    if not self.audiobook.volume:
                        self.audiobook.volume = number
