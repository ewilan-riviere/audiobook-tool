"""Parse Audible web output"""

from typing import List, cast
from bs4 import BeautifulSoup
from audiobook.common import AutoRepr
from audiobook.audible.typed import AudibleHtml


class ParserHtml(AutoRepr):
    """Parse Audible HTML"""

    def __init__(self, soup: BeautifulSoup):
        self._soup = soup
        self.html = cast(AudibleHtml, {})

        self.html["title"] = self._parse_soup("h1", "title")
        self.html["subtitle"] = self._parse_soup("h2", "subtitle")
        description = self._parse_description()
        self.html["description"] = description["description"]
        self.html["copyright"] = description["copyright"]
        self.html["genres"] = self._parse_genres()

    def _parse_genres(self) -> List[str]:
        """Extract genres"""
        genres_labels: List[str] = []

        if self._soup:
            tags = self._soup.find_all("adbl-chip")

            for tag in tags:
                text = tag.get_text().strip()
                if text:
                    genres_labels.append(text)

        if len(genres_labels) > 0:
            genres_labels.pop()

        return genres_labels

    def _parse_description(self) -> dict[str, str]:
        data = {"description": "", "copyright": ""}
        if self._soup:
            description_html = self._soup.find(
                "adbl-text-block",
                attrs={"slot": "summary"},
            )
            if description_html:
                paragraphs = [
                    p.get_text().strip() for p in description_html.find_all("p")
                ]
                data["description"] = "\n\n".join(paragraphs)

                full_text = description_html.get_text(separator="|", strip=True)
                parts = full_text.split("|")
                if parts:
                    data["copyright"] = parts[-1].strip()

        return data

    def _parse_soup(self, name: str, attrs_value: str, attrs_name: str = "slot"):
        if self._soup:
            tag = self._soup.find(name, attrs={attrs_name: attrs_value})
            if tag:
                return tag.get_text().strip()
        return None
