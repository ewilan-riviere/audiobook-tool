"""Parse Audible `application/json`"""

from typing import cast
import json
import re
from datetime import time, datetime
from bs4 import BeautifulSoup, Tag
from audiobook.common import AutoRepr
from audiobook.audible.types import (
    JsonAudiobook,
    JsonLdAudiobook,
    JsonLdProduct,
)
from .data_object import DataObject


class ParserJson(AutoRepr):
    """Parse Audible `application/json`"""

    def __init__(self, soup: BeautifulSoup):
        self._soup = soup

        jsonld_scripts = self._soup.find_all("script", type="application/ld+json")
        json_scripts = self._soup.find_all("script", type="application/json")

        jsonld_data = self._convert_json(jsonld_scripts)
        self.ld_audiobook = self._convert_ld_audiobook(jsonld_data)
        self.ld_product = self._convert_ld_product(jsonld_data)

        json_data = self._convert_json(json_scripts)
        self.audiobook = self._convert_audiobook(json_data)

    def _convert_audiobook(self, data: list[DataObject]) -> JsonAudiobook:
        authors = self._find_data_by_attr(data, "authors")
        language = self._find_data_by_attr(data, "language")
        item = cast(JsonAudiobook, {})

        if not authors or not language:
            return item

        item["authors"] = self._to_list(authors.deep("authors"), "name")
        item["narrators"] = self._to_list(authors.deep("narrators"), "name")
        item["release_date"] = language.deep("releaseDate")
        item["series"] = self._to_list(language.deep("series"), "name")
        parts = self._to_list(language.deep("series"), "part")
        if parts:
            item["part"] = parts[0]
        item["duration"] = language.deep("duration")
        item["rating"] = self._to_float(authors.deep("rating.value"))
        item["format"] = language.deep("format")
        item["publisher"] = language.deep("publisher.name")
        item["language"] = language.deep("language")
        item["categories"] = self._to_list(language.deep("categories"), "name")

        return item

    def _convert_ld_product(self, listing: list[DataObject]) -> JsonLdProduct:
        data = self._find_data_ld(listing, "type", "Product")
        item = cast(JsonLdProduct, {})

        if not data:
            return item

        item["context"] = data.context
        item["type"] = data.type
        item["additional_type"] = data.additionalType
        item["product_id"] = data.productID
        item["name"] = data.name
        item["image"] = data.image
        item["sku"] = data.sku
        item["brand"] = data.brand
        item["rating"] = self._to_float(data.deep("aggregateRating.ratingValue"))
        item["price"] = self._to_float(data.deep("offers.price"))

        return item

    def _convert_ld_audiobook(self, listing: list[DataObject]) -> JsonLdAudiobook:
        data = self._find_data_ld(listing, "type", "Audiobook")
        item = cast(JsonLdAudiobook, {})

        if not data:
            return item

        item["context"] = data.context
        item["type"] = data.type
        item["book_format"] = data.bookFormat
        item["name"] = data.name
        item["description"] = data.description
        item["image"] = data.image
        item["abridged"] = self._to_bool(data.deep("abridged"))
        item["author"] = self._to_list(data.author, "name")
        item["read_by"] = self._to_list(data.readBy, "name")
        item["publisher"] = data.publisher
        date_published = data.datePublished
        if date_published:
            item["date_published"] = datetime.strptime(
                date_published, "%Y-%m-%d"
            ).date()
        item["in_language"] = data.inLanguage
        item["duration"] = self._to_duration(data.duration)
        item["regions_allowed"] = data.regionsAllowed
        item["rating"] = self._to_float(data.deep("aggregateRating.ratingValue"))
        item["price"] = self._to_float(data.deep("offers.price"))

        return item

    def _convert_json(self, scripts: list[Tag]) -> list[DataObject]:
        """Convert <script type=`application/json`> into JSON"""
        data: list[DataObject] = []
        for script in scripts:
            if not script.string:
                continue

            raw_json = json.loads(script.string)

            if isinstance(raw_json, list):
                data.extend([DataObject(item) for item in raw_json])  # type: ignore
            else:
                data.append(DataObject(raw_json))  # type: ignore

        return data

    def _find_data_ld(
        self,
        data: list[DataObject],
        key: str,
        name: str,
    ) -> DataObject | None:
        """Find specific `DataObject` into a `list`"""
        items: list[DataObject] = [
            item for item in data if getattr(item, key, None) == name
        ]

        if items:
            return items[0]

        return None

    def _find_data_by_attr(
        self,
        items: list[DataObject],
        attr_name: str,
    ) -> DataObject | None:
        """Find `DataObject` with attribute name"""
        return next(
            (item for item in items if getattr(item, attr_name, None) is not None),
            None,
        )

    def _to_float(self, value: str | None) -> float | None:
        """Convert `str` to `float`"""
        if not value:
            return None

        val = float(value)
        return round(val, 2)

    def _to_bool(self, value: str | None) -> bool:
        """Convert `str` to `bool`"""
        if not value:
            return False

        return value.lower() in ("true", "1", "yes", "t")

    def _to_list(self, items: list[DataObject] | None, key: str) -> list[str] | None:
        """Parse a `list` of `DataObject` to create a `list` of `str`"""
        if not items:
            return None

        listing: list[str] = []
        for item in items:
            value = getattr(item, key, None)
            if value:
                listing.append(value)

        return listing

    def _to_duration(self, iso: str | None) -> time | None:
        """Parse ISO 8601 to time"""
        if not iso:
            return None

        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso)

        if not match:
            return None

        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)

        return time(hour=h, minute=m)
