"""Parse Audible `application/json`"""

import html
import json
from typing import Any
from playwright.sync_api import Page
from ..types import LDAudiobook, LDProduct, JsonDuration, JsonRating


class ParserJson:
    """Parse Audible `application/json`"""

    def __init__(self, page: Page):
        ld_json_data = self._parse(page, 'script[type="application/ld+json"]')
        json_data = self._parse(page, 'script[type="application/json"]')

        ld_audiobook = self._find_json_ld(ld_json_data, "Audiobook")
        ld_product = self._find_json_ld(ld_json_data, "Product")

        json_duration = self._find_json(json_data, "duration")
        json_rating = self._find_json(json_data, "rating")

        self.ld_audiobook = self._handle_ld_audiobook(ld_audiobook)
        self.ld_product = self._handle_ld_product(ld_product)

        self.json_duration = self._handle_json_duration(json_duration)
        self.json_rating = self._handle_json_rating(json_rating)

    def _handle_json_rating(self, script: dict[str, Any] | None) -> JsonRating:
        if not script:
            return JsonRating()

        rating: dict[str, Any] = script.get("rating", {})
        return JsonRating(
            rating_count=rating.get("count"),
            rating_value=rating.get("value"),
            authors=self._extract_list(script.get("authors"), "name"),
            narrators=self._extract_list(script.get("narrators"), "name"),
        )

    def _handle_json_duration(self, script: dict[str, Any] | None) -> JsonDuration:
        if not script:
            return JsonDuration()

        part = None
        parts = self._extract_list(script.get("series"), "part")
        if parts:
            part = parts[0]
        publisher: dict[str, Any] = script.get("publisher", {})

        return JsonDuration(
            duration=script.get("duration"),
            release_date=script.get("releaseDate"),
            series=self._extract_list(script.get("series"), "name"),
            part=part,
            format_=script.get("format"),
            publisher=publisher.get("name"),
            language=script.get("language"),
            categories=self._extract_list(script.get("categories"), "name"),
        )

    def _handle_ld_product(self, product: dict[str, Any] | None) -> LDProduct:
        if not product:
            return LDProduct()

        rating: dict[str, Any] = product.get("aggregateRating", {})
        offers: dict[str, Any] = product.get("offers", {})
        return LDProduct(
            context=product.get("@context"),
            type_=product.get("@type"),
            additional_type=product.get("additionalType"),
            product_id=product.get("productID"),
            name=product.get("name"),
            image=product.get("image"),
            sku=product.get("sku"),
            brand=product.get("brand"),
            rating_value=rating.get("ratingValue"),
            rating_count=rating.get("ratingCount"),
            price=offers.get("price"),
            currency=offers.get("priceCurrency"),
        )

    def _handle_ld_audiobook(self, audiobook: dict[str, Any] | None) -> LDAudiobook:
        if not audiobook:
            return LDAudiobook()

        rating: dict[str, Any] = audiobook.get("aggregateRating", {})
        offers: dict[str, Any] = audiobook.get("offers", {})
        return LDAudiobook(
            context=audiobook.get("@context"),
            type_=audiobook.get("@type"),
            book_format=audiobook.get("bookFormat"),
            name=audiobook.get("name"),
            description=audiobook.get("description"),
            image=audiobook.get("image"),
            abridged=audiobook.get("abridged"),
            author=self._extract_list(audiobook.get("author"), "name"),
            read_by=self._extract_list(audiobook.get("readBy"), "name"),
            publisher=audiobook.get("publisher"),
            date_published=audiobook.get("datePublished"),
            in_language=audiobook.get("inLanguage"),
            duration=audiobook.get("duration"),
            regions_allowed=audiobook.get("regionsAllowed"),
            rating_value=rating.get("ratingValue"),
            rating_count=rating.get("ratingCount"),
            price=offers.get("price"),
            currency=offers.get("priceCurrency"),
        )

    def _extract_list(self, list_: list[dict[str, str]] | None, key: str) -> list[str]:
        items: list[str] = []
        if not list_:
            return items

        for item in list_:
            value = item.get(key)
            if value:
                items.append(value)

        return items

    def _parse(self, page: Page, selector: str) -> list[dict[str, Any]]:
        """Get scripts from HTML"""
        results: list[dict[str, Any]] = []
        scripts = page.locator(selector).all_inner_texts()

        for s in scripts:
            try:
                decoded_s = html.unescape(s)
                data = json.loads(decoded_s)

                if isinstance(data, list):
                    results.extend(data)  # type: ignore
                else:
                    results.append(data)
            except json.JSONDecodeError:
                continue

        return results

    def _find_json_ld(
        self,
        script: list[dict[str, Any]],
        schema_type: str,
    ) -> dict[str, Any] | None:
        """
        Find LD JSON by `@type`
        can be `Organization`, `Audiobook`, `BreadcrumbList` or `Product`
        """
        items = [item for item in script if item.get("@type") == schema_type]
        if items:
            return items[0]

        return None

    def _find_json(
        self,
        script: list[dict[str, Any]],
        key: str,
    ) -> dict[str, Any] | None:
        """
        Find JSON by key
        can be `duration`, `rating`
        """
        return next((item for item in script if key in item), None)
