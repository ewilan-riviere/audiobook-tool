"""Parse Audible HTML web output"""

import re
import unicodedata
from playwright.sync_api import Page, Locator
from audiobook.audible.types import AudibleHtml


class ParserHtml:
    """Parse Audible HTML web output"""

    def __init__(self, page: Page):
        data = self._parse(page)
        genres = self._parse_genres(page)
        self.content: AudibleHtml = AudibleHtml(
            title=data["title"],
            subtitle=data["subtitle"],
            description=data["description"],
            synopsis=data["synopsis"],
            copyright_=data["copyright_"],
            genres=genres,
            rating_value=data["rating_value"],
            rating_count=data["rating_count"],
            image_url=data["image_url"],
        )

    def _parse(self, page: Page):
        rating_locator = page.locator('[data-testid="star-rating"]')

        image_url = self._extract_attribute(
            page.locator("adbl-product-image img"), "src"
        )
        rating_value = self._extract_attribute(rating_locator, "value")
        rating_count = self._extract_attribute(rating_locator, "count")
        title = self._extract_text(page.locator('h1[slot="title"]'))
        subtitle = self._extract_text(page.locator('h2[slot="subtitle"]'))
        description = self._extract_text(
            page.locator('adbl-text-block[slot="summary"]')
        )

        synopsis_ = None
        copyright_ = None
        if description:
            desc = self._split_description(description)
            synopsis_ = desc["synopsis"]
            copyright_ = desc["copyright"]

        data: dict[str, str | None] = {
            "title": self._clean_text(title),
            "subtitle": self._clean_text(subtitle),
            "description": description,
            "synopsis": synopsis_,
            "copyright_": copyright_,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "image_url": image_url,
        }

        return data

    def _parse_genres(self, page: Page) -> list[str] | None:
        genres_locator = page.locator("adbl-chip").filter(
            has_not_text=re.compile(r"Tout|All", re.I)
        )

        genres = None
        if genres_locator.count() > 0:
            genres = genres_locator.all_text_contents()

        items: list[str] = []
        if not genres:
            return None

        for genre in genres:
            value = self._clean_text(genre)
            if value:
                items.append(value)

        items.sort()

        return items

    def _extract_text(self, locator: Locator) -> str | None:
        value = None
        if locator.count() > 0:
            value = locator.inner_text()
            value = self._clean_text(value)

        return value

    def _extract_attribute(self, locator: Locator, attr: str) -> str | None:
        value = None
        if locator.count() > 0:
            value = locator.get_attribute(attr)

        return value

    def _split_description(self, text: str) -> dict[str, str | None]:
        match = re.search(r"(.*)(©.*)", text, re.DOTALL)
        synopsis_ = None
        copyright_ = None
        if match:
            synopsis_ = match.group(1).strip()
            copyright_ = match.group(2).strip()

        return {"synopsis": synopsis_, "copyright": copyright_}

    def _clean_text(self, text: str | None) -> str | None:
        if not text:
            return None

        text = text.encode().decode("unicode_escape")
        text = text.encode("latin1").decode("utf-8")
        text = text.strip('"')
        text = text.replace(" . . .", "...")
        text = unicodedata.normalize("NFKC", text)
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")

        return text
