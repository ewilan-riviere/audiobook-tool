"""Parse Audible JSON LD to get metadata"""

import html
import json
from typing import Dict, Any, cast
import re
from datetime import datetime, time
import isodate  # type: ignore
import httpx
from bs4 import BeautifulSoup
from audiobook.common import AutoRepr


class AudibleParserJsonLD(AutoRepr):
    """Parse Audible JSON LD to get metadata"""

    def __init__(self, asin: str, output_cover: str | None = None):
        self._asin = asin
        self.url: str | None = None
        self._jsonld_raw: dict[str, Any] | None = None
        self._output_cover = output_cover
        self.jsonld_found = False
        self.json_ld: Dict[str, Any] = {}
        # self.audiobook: AudibleMetadata | None = None

        # https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html
        for suffix in ["fr", "com", "co.uk", "de"]:
            self._parse_url(suffix)

        if self._jsonld_raw:
            self.json_ld = self._parse_jsonld_raw()
        else:
            print(f"Error: no metadata found for ASIN {self._asin}.")

    def _parse_jsonld_raw(self) -> Dict[str, Any]:
        json_ld: Dict[str, Any] = {}

        json_ld["asin"] = self._asin
        json_ld["title"] = self._extract("name")
        json_ld["description"] = None
        json_ld["authors"] = self._extract_people("author")
        json_ld["narrators"] = self._extract_people("readBy")
        json_ld["release_date"] = None
        json_ld["duration_human"] = self._duration_human(self._extract("duration"))
        json_ld["duration_time"] = self._duration_time(self._extract("duration"))
        json_ld["rating"] = self._handle_rating("aggregateRating")
        json_ld["cover_url"] = self._extract("image")
        json_ld["publisher"] = self._extract("publisher")
        json_ld["language"] = self._extract("inLanguage")
        json_ld["is_abridged"] = self._extract("abridged") == "true"

        description = self._extract("description")
        if description:
            json_ld["description"] = description.replace("\n", "\n\n")

        release_date = self._extract("datePublished")
        if release_date:
            json_ld["release_date"] = datetime.strptime(release_date, "%Y-%m-%d")

        return json_ld

    def _extract(self, key: str) -> str | None:
        """Extract key fron JSON LD as `str`"""
        if not self._jsonld_raw:
            return None

        value = str(self._jsonld_raw.get(key, ""))
        value = self._clean_text(value)

        return self._clean_text(value)

    def _extract_people(self, key: str) -> list[str] | None:
        """Extract key fron JSON LD as `list[str]`"""
        if not self._jsonld_raw:
            return None

        values = self._jsonld_raw.get(key, [])
        if not isinstance(values, list):
            values = [values]

        values_list = cast(list[dict[str, Any]], values)
        final_list = [str(a.get("name", "")) for a in values_list]

        items: list[str] = []
        for v in final_list:
            items.append(self._clean_text(v))

        return items

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

    def _clean_value(self, value: str | None):
        if not value:
            return None

        return html.unescape(value)

    def _handle_rating(self, key: str):
        """Handle rating"""
        if not self._jsonld_raw:
            return None

        rating = self._jsonld_raw.get(key)
        if isinstance(rating, dict):
            try:
                return round(float(rating.get("ratingValue", 0)), 1)  # type: ignore
            except (ValueError, TypeError):
                return None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        # Replace paragraph breaks with line breaks
        # We manage </p>, <br>, </div>, etc.
        text = re.sub(r"</p>|<br\s*/?>|</div>", "\n", text)

        # Remove all other HTML tags
        clean = re.compile("<.*?>")
        text = re.sub(clean, "", text)

        # Unescape, strip, and clean up unnecessary empty lines
        text = html.unescape(text).strip()

        # Optional: avoid having 4 line breaks if the HTML was complex
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    def _parse_url(self, locale: str = "com") -> dict[str, Any] | None:
        """Parse Audible to extract JSON LD"""
        url = f"https://www.audible.{locale}/pd/{self._asin}"

        # Cookies are added to “fix” the location to the US.
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

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error: {e}")

        if jsonld:
            self._jsonld_raw = jsonld
            self.jsonld_found = True
            self.url = url

            return jsonld  # type: ignore

        return None
