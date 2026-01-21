"""Parse Audible JSON LD to get metadata"""

import html
import json
from typing import Any, cast
import re
from datetime import datetime, time
import isodate  # type: ignore
import httpx
from bs4 import BeautifulSoup
from .metadata import AudibleMetadata
from .parser import AudibleParser


class AudibleJson:
    """Parse Audible JSON LD to get metadata"""

    def __init__(self, asin: str):
        self._asin = asin
        self._url_valid: str | None = None
        self._jsonld: dict[str, Any] | None = None
        self.jsonld_found = False
        self.audiobook: AudibleMetadata | None = None

        # https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html
        for suffix in ["fr", "com", "co.uk", "de"]:
            self._parse_audible(suffix)

        if self._jsonld:
            self.audiobook = self._parse_jsonld()
            self._parse_web()
        else:
            print(f"Error: no metadata found for ASIN {self._asin}.")

    def _parse_jsonld(self) -> AudibleMetadata:
        audiobook = AudibleMetadata()

        audiobook.asin = self._asin
        audiobook.title = self._extract("name")
        audiobook.description = self._extract("description")
        audiobook.authors = self._extract_people("author")
        audiobook.narrators = self._extract_people("readBy")

        release_date = self._extract("datePublished")
        if release_date:
            audiobook.release_date = datetime.strptime(release_date, "%Y-%m-%d")

        audiobook.duration_human = self._duration_human(self._extract("duration"))
        audiobook.duration_time = self._duration_time(self._extract("duration"))
        audiobook.rating = self._handle_rating("aggregateRating")
        audiobook.cover_url = self._extract("image")
        audiobook.publisher = self._extract("publisher")
        audiobook.language = self._extract("inLanguage")
        audiobook.is_abridged = self._extract("abridged") == "true"

        audiobook.save_cover("cover.jpg")

        return audiobook

    def _parse_web(self):
        if not self._url_valid:
            return self

        parser = AudibleParser(self._url_valid)

        if self.audiobook:
            self.audiobook.series = parser.series_name_alt
            self.audiobook.volume = parser.volume
            self.audiobook.genres = parser.genres

    def _extract(self, key: str) -> str | None:
        """Extract key fron JSON LD as `str`"""
        if not self._jsonld:
            return None

        value = str(self._jsonld.get(key, ""))
        value = self._clean_text(value)

        return value

    def _extract_people(self, key: str) -> list[str] | None:
        """Extract key fron JSON LD as `list[str]`"""
        if not self._jsonld:
            return None

        values = self._jsonld.get(key, [])
        if not isinstance(values, list):
            values = [values]

        values_list = cast(list[dict[str, Any]], values)
        final_list = [str(a.get("name", "")) for a in values_list]

        return final_list

    def _duration_human(self, iso_duration: str | None) -> str | None:
        """Parse ISO 8601 to human duration"""
        if not iso_duration:
            return None

        return (
            iso_duration.replace("PT", "").replace("H", "h ").replace("M", "m").strip()
        )

    def _duration_time(self, iso_duration: str | None) -> time | None:
        """Parse ISO 8601 to time"""
        if not iso_duration:
            return None

        duration = isodate.parse_duration(iso_duration)  # type: ignore
        return (datetime.min + duration).time()  # type: ignore

    def _handle_rating(self, key: str):
        """Handle rating"""
        if not self._jsonld:
            return None

        rating = self._jsonld.get(key)
        if isinstance(rating, dict):
            try:
                return round(float(rating.get("ratingValue", 0)), 1)  # type: ignore
            except (ValueError, TypeError):
                return None

    def _clean_text(self, text: str) -> str:
        """Clean JSON LD text"""
        if not text:
            return ""

        clean = re.compile("<.*?>")
        text = re.sub(clean, "", text)

        return html.unescape(text).strip()

    def _parse_audible(self, locale: str = "com") -> dict[str, Any] | None:
        """Parse Audible to extract JSON LD"""
        url = f"https://www.audible.{locale}/pd/{self._asin}"

        # On ajoute des cookies pour "fixer" la localisation sur US
        cookies = {"lc-main-av": "en_US"}
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": f"https://www.audible.{locale}/",
        }

        jsonld = None

        try:
            with httpx.Client(
                headers=headers,
                cookies=cookies,
                follow_redirects=True,
                timeout=15,
            ) as client:
                resp = client.get(url)

                # Check if the URL contains “pd/{asin} or if it redirected you to the home page
                # print(f"Loaded URL : {resp.url}")

                soup = BeautifulSoup(resp.text, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")

                for s in scripts:
                    if not s.string:
                        continue
                    try:
                        data = json.loads(s.string)

                        # JSON-LD can be a direct object or a list of objects.
                        items = data if isinstance(data, list) else [data]  # type: ignore

                        for item in items:  # type: ignore
                            if item.get("@type") == "Audiobook":  # type: ignore
                                jsonld = item  # type: ignore

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Error: {e}")

        if jsonld:
            self._jsonld = jsonld
            self.jsonld_found = True
            self._url_valid = url

            return jsonld  # type: ignore
        else:
            print(f"Not found on `{url}`")

        return None
