"""Fetch metadata from Audible from audiobook ASIN"""

from pathlib import Path
from audiobook.common import AutoRepr
from audiobook.models import AudibleAudiobook
from audiobook.yml import YmlWriter
from .fetch import AudibleFetch


class Audible(AutoRepr):
    """Fetch metadata from Audible from audiobook ASIN"""

    success: bool = False

    def __init__(self, asin: str, locale: str | None = None):
        self.fetch = AudibleFetch(asin, locale)
        self.audiobook = AudibleAudiobook(asin)

        if not self.fetch.success:
            return

        if not self.fetch.url:
            return

        self.audiobook.url = self.fetch.url
        self.success = self.fetch.success
        self._handle_audiobook()

    def save_metadata(self, save_path: str | Path) -> str:
        """Save audiobook as metadata.yml"""
        save_path = Path(save_path).resolve()
        writer = YmlWriter(self.audiobook, save_path)
        writer.write()

        return str(writer.save_path)

    def _handle_audiobook(self):
        ld_audiobook = self.fetch.ld_audiobook
        ld_product = self.fetch.ld_product
        html = self.fetch.html
        json_duration = self.fetch.json_duration
        json_rating = self.fetch.json_rating
        extra = self.fetch.extra

        self.audiobook.original_title = ld_audiobook.name
        self.audiobook.original_series = json_duration.series

        self.audiobook.subtitle = html.subtitle
        self.audiobook.description = html.synopsis
        self.audiobook.copyright_ = html.copyright_
        self.audiobook.publisher = ld_audiobook.publisher

        self.audiobook.authors = json_rating.authors_typed
        self.audiobook.narrators = json_rating.narrators

        self.audiobook.published_at = ld_audiobook.date_published_typed
        self.audiobook.duration = ld_audiobook.duration_typed
        language = ld_audiobook.in_language
        if language:
            self.audiobook.language = language.capitalize()
        self.audiobook.abridged = ld_audiobook.abridged_typed
        self.audiobook.cover = ld_audiobook.image

        self.audiobook.volume = extra.volume_typed
        self.audiobook.part = json_duration.part
        self.audiobook.title = extra.title_typed
        self.audiobook.series = extra.series_typed

        self.audiobook.format_ = json_duration.format_
        self.audiobook.book_format = ld_audiobook.book_format
        self.audiobook.sku = ld_product.sku
        self.audiobook.product_id = ld_product.product_id

        self.audiobook.rating = json_rating.rating_value
        self.audiobook.price = ld_product.price_typed
        self.audiobook.currency = ld_product.currency

        self.audiobook.genres = html.genres
        self.audiobook.categories = json_duration.categories

        return self.audiobook
