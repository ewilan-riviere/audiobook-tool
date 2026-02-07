"""Parse Audible web output"""

from typing import List, Optional, cast
import json
import requests
from bs4 import BeautifulSoup, Tag
from .typed import AudibleHtml, AudibleJson
from audiobook.common import AutoRepr


class ParserWeb(AutoRepr):
    """Parse Audible web output"""

    html: AudibleHtml | None = None
    json: AudibleJson | None = None

    def __init__(self, url: str):
        self.url = url
        self._soup: Optional[BeautifulSoup] = None

        html = self._extract_html()
        if not html:
            return

        self._soup = BeautifulSoup(html, "html.parser")
        self.html = self._parse_html()
        self.json = self._parse_json()
        self._soup = None

    def _parse_html(self) -> AudibleHtml:
        data = cast(AudibleHtml, {})

        data["title"] = self._parse_soup("h1", "title")
        data["subtitle"] = self._parse_soup("h2", "subtitle")
        description = self._parse_description()
        data["description"] = description["description"]
        data["copyright"] = description["copyright"]
        data["genres"] = self._parse_genres()

        return data

    def _parse_json(self) -> AudibleJson:
        data = cast(AudibleJson, {})
        if not self._soup:
            return data

        json_scripts = self._soup.find_all("script", type="application/json")

        if len(json_scripts) != 2:
            raise Exception(  # pylint: disable=broad-exception-raised
                "Audible should provide only 2 scripts."
            )

        rating_json = json_scripts[0]
        metadata_json = json_scripts[1]
        data["series"] = self._parse_tag(metadata_json, "series", "name")
        data["duration"] = self._parse_tag(metadata_json, "duration")
        data["realease_date"] = self._parse_tag(metadata_json, "releaseDate")
        data["rating"] = self._parse_tag(rating_json, "rating", "value")
        data["format"] = self._parse_tag(metadata_json, "format")
        data["publisher"] = self._parse_tag(metadata_json, "publisher", "name")
        data["language"] = self._parse_tag(metadata_json, "language")
        data["categories"] = self._parse_tag(metadata_json, "categories", "name")

        return data

    def _parse_tag(self, script: Tag, key: str, name: str | None = None) -> str | None:
        if not script.string:
            return None

        try:
            script_data = json.loads(script.string)
            value = script_data.get(key, [])
            if isinstance(value, str):
                return value
            elif isinstance(value, dict):
                return value[name]  # type: ignore
            elif isinstance(value, list):
                return value[0].get(name)  # type: ignore

            return None
        except (json.JSONDecodeError, KeyError, IndexError):
            return None

    def _parse_genres(self) -> List[str]:
        """Extract genres"""
        genres_labels: List[str] = []

        if self._soup:
            # We are looking for all <adbl-chip>
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

    def _extract_html(self) -> str | None:
        if not self.url:
            return None

        try:
            _session = requests.Session()
            # _session.headers.update()
            res = _session.get(self.url, timeout=15)

            if res.status_code == 503:
                print("Error 503: blocked by anti-bot (CAPTCHA)")
                return None

            res.raise_for_status()

            return res.text

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")

        return None
