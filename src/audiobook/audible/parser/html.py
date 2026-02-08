"""Parse Audible web output"""

from typing import List, cast
import re
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
        if not self._soup:
            return data

        description_html = self._soup.find("adbl-text-block", attrs={"slot": "summary"})

        if description_html:
            # 1. Clean up paragraphs for the description
            paragraphs = [p.get_text().strip() for p in description_html.find_all("p")]
            # Filter out paragraphs that look like copyright strings
            description_parts = [p for p in paragraphs if not re.match(r"^©|\(P\)", p)]

            description = "\n\n".join(description_parts)
            data["description"] = description.replace(" . . .", "...")

            # 2. Specifically look for the copyright string
            # We look through all paragraphs for the one containing the copyright symbols
            full_text_content = description_html.get_text("\n").split("\n")
            for line in reversed(full_text_content):
                line = line.strip()
                if re.search(r"©\d{4}|\(P\)\d{4}", line):
                    data["copyright"] = line
                    break

        return data

    def _parse_soup(self, name: str, attrs_value: str, attrs_name: str = "slot"):
        if self._soup:
            tag = self._soup.find(name, attrs={attrs_name: attrs_value})
            if tag:
                return tag.get_text().strip()
        return None
