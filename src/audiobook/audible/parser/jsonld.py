from typing import Any, Dict, cast
import json
import re
import html
from datetime import datetime, time
import isodate  # type: ignore
from bs4 import Tag
from audiobook.common import AutoRepr
from .typed import AudibleJsonld


class ParserJsonld(AutoRepr):
    raw: Dict[str, Any] | None = None
    jsonld: AudibleJsonld | None = None

    def __init__(self, tags: list[Tag] | None):
        if tags:
            for tag in tags:
                data = self._parse_tags(tag)
                if data:
                    self.raw = data

        if self.raw:
            self.jsonld = self._parse_jsonld()

    def _parse_tags(self, tag: Tag) -> Dict[str, Any] | None:
        if not tag.string:
            return None

        jsonld: dict[str, Any] | None = None
        try:
            data = json.loads(tag.string)

            # JSON-LD can be a direct object or a list of objects.
            items = data if isinstance(data, list) else [data]  # type: ignore

            for item in items:  # type: ignore
                if item.get("@type") == "Audiobook":  # type: ignore
                    jsonld = item  # type: ignore

        except json.JSONDecodeError:
            return None

        return jsonld  # type: ignore

    def _parse_jsonld(self) -> AudibleJsonld:
        data = cast(AudibleJsonld, {})

        data["title"] = self._extract("name")
        data["description"] = None
        data["authors"] = self._extract_people("author")
        data["narrators"] = self._extract_people("readBy")
        data["release_date"] = None
        data["duration_human"] = self._extract_duration_human()
        data["duration_time"] = self._extract_duration()
        data["rating"] = self._handle_rating("aggregateRating")
        data["cover_url"] = self._extract("image")
        data["publisher"] = self._extract("publisher")
        data["language"] = self._extract("inLanguage")
        data["is_abridged"] = self._extract("abridged") == "true"

        description = self._extract("description")
        if description:
            data["description"] = description.replace("\n", "\n\n")

        release_date = self._extract("datePublished")
        if release_date:
            data["release_date"] = datetime.strptime(release_date, "%Y-%m-%d")

        return data

    def _extract(self, key: str) -> str | None:
        """Extract key fron JSON LD as `str`"""
        if not self.raw:
            return None

        value = str(self.raw.get(key, ""))
        value = self._clean_text(value)

        return self._clean_text(value)

    def _extract_people(self, key: str) -> list[str] | None:
        """Extract key fron JSON LD as `list[str]`"""
        if not self.raw:
            return None

        values = self.raw.get(key, [])
        if not isinstance(values, list):
            values = [values]

        values_list = cast(list[dict[str, Any]], values)
        final_list = [str(a.get("name", "")) for a in values_list]

        items: list[str] = []
        for v in final_list:
            items.append(self._clean_text(v))

        return items

    def _extract_duration_human(self) -> str | None:
        """Parse ISO 8601 to human duration"""
        iso_duration = self._extract("duration")
        if not iso_duration:
            return None

        return (
            iso_duration.replace("PT", "").replace("H", "h ").replace("M", "m").strip()
        )

    def _extract_duration(self) -> time | None:
        """Parse ISO 8601 to time"""
        iso_duration = self._extract("duration")
        if not iso_duration:
            return None

        duration = isodate.parse_duration(iso_duration)  # type: ignore
        return (datetime.min + duration).time()  # type: ignore

    def _handle_rating(self, key: str):
        """Handle rating"""
        if not self.raw:
            return None

        rating = self.raw.get(key)
        if isinstance(rating, dict):
            rating_value = rating.get("ratingValue", 0)  # type: ignore
            if not rating_value:
                return None
            try:
                return round(float(rating_value), 1)  # type: ignore
            except (ValueError, TypeError):
                return None

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""

        # Replace paragraph breaks with line breaks
        text = re.sub(r"</p>|<br\s*/?>|</div>", "\n", text)

        # Remove all other HTML tags
        clean = re.compile("<.*?>")
        text = re.sub(clean, "", text)

        # Unescape, strip, and clean up unnecessary empty lines
        text = html.unescape(text).strip()

        # Optional: avoid having 4 line breaks if the HTML was complex
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())
