"""Fetch metadata from Audible from audiobook ASIN"""

import re
from audiobook.common import AutoRepr
from .parser import ParserJson, ParserHtml
from .typed import JsonAudiobook
from .audiobook import AudibleAudiobook
from .fetch import AudibleFetch
from .template import TemplateYml


class Audible(AutoRepr):
    """Fetch metadata from Audible from audiobook ASIN"""

    success: bool = False

    def __init__(self, asin: str, locale: str | None = None):
        fetch = AudibleFetch(asin, locale)
        self.audiobook = AudibleAudiobook(asin)

        if not fetch.success:
            return

        if not fetch.soup or not fetch.url:
            return

        self.audiobook.url = fetch.url
        web = ParserHtml(fetch.soup)
        json = ParserJson(fetch.soup)
        self._handle_audiobook(web, json)
        self.success = True

    def save_metadata(self, save_path: str) -> str:
        """Save audiobook as metadata.yml"""
        yml = TemplateYml(self.audiobook, save_path)

        return str(yml.save_path)

    def _handle_audiobook(self, web: ParserHtml, json: ParserJson):
        self.audiobook.title = web.html.get("title")
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

        self._handle_series(json.audiobook)
        self.audiobook.format = json.audiobook.get("format")
        self.audiobook.book_format = json.ld_audiobook.get("book_format")
        self.audiobook.sku = json.ld_product["sku"]

        self.audiobook.rating = json.audiobook.get("rating")
        self.audiobook.price = json.ld_audiobook.get("price")

        self.audiobook.genres = web.html.get("genres")
        self.audiobook.categories = json.audiobook.get("categories")

        self.audiobook.title_clean = None
        self.audiobook.series_clean = None
        self.audiobook.volume_clean = None

        clean = self.audiobook.clean()
        if clean.get("title"):
            self.audiobook.title_clean = str(clean.get("title"))
        if clean.get("series"):
            self.audiobook.series_clean = str(clean.get("series"))
        if clean.get("volume"):
            volume = clean.get("volume")
            if volume:
                self.audiobook.volume_clean = float(volume)

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
        self.audiobook.series = audio.get("series")
        if self.audiobook.series:
            self.audiobook.series_main = self.audiobook.series[0]

            self.audiobook.part = audio.get("part")
            self.audiobook.volume = None

            if self.audiobook.part:
                match = re.search(r"\d+", self.audiobook.part)
                if match:
                    number = int(match.group())
                    if not self.audiobook.volume:
                        self.audiobook.volume = number
