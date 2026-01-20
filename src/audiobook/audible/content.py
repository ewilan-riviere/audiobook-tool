import html
import json
import re
from datetime import datetime
from typing import Any, cast
import httpx
from bs4 import BeautifulSoup


class AudibleContent:
    def __init__(self, asin: str):
        self._asin = asin
        self.title: str = ""
        self.authors: list[str] = []
        self.narrators: list[str] = []
        self.description: str = ""
        self.release_date: datetime | None = None
        self.duration: str = ""
        self.rating: float = 0.0
        self.cover_url: str = ""
        self.publisher: str = ""
        self.language: str = ""
        self.is_abridged: bool = False

        data = self._fetch_metadata()
        if data:
            self._parse_data(data)

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        clean = re.compile("<.*?>")
        text = re.sub(clean, "", text)
        return html.unescape(text).strip()

    def _format_duration(self, iso_duration: str) -> str:
        if not iso_duration:
            return ""
        return (
            iso_duration.replace("PT", "").replace("H", "h ").replace("M", "m").strip()
        )

    def _parse_data(self, data: dict[str, Any]) -> None:
        self.title = self._clean_text(str(data.get("name", "")))
        self.description = self._clean_text(str(data.get("description", "")))

        # --- AUTEURS ---
        authors_raw = data.get("author", [])
        if not isinstance(authors_raw, list):
            authors_raw = [authors_raw]

        # On cast une fois pour toutes
        authors_list = cast(list[dict[str, Any]], authors_raw)
        # On fait confiance au cast : pas besoin de isinstance ici
        self.authors = [str(a.get("name", "")) for a in authors_list]

        # --- NARRATEURS ---
        narrators_raw = data.get("readBy", [])
        if not isinstance(narrators_raw, list):
            narrators_raw = [narrators_raw]

        narrators_list = cast(list[dict[str, Any]], narrators_raw)
        self.narrators = [str(n.get("name", "")) for n in narrators_list]

        # --- AUTRES INFOS ---
        release_date = str(data.get("datePublished", ""))
        if release_date:
            self.release_date = datetime.strptime(release_date, "%Y-%m-%d")
        self.duration = self._format_duration(str(data.get("duration", "")))

        # Pour le rating, on garde le isinstance car rating_obj est "Any"
        rating_obj = data.get("aggregateRating")
        if isinstance(rating_obj, dict):
            try:
                self.rating = round(
                    float(rating_obj.get("ratingValue", 0)), 1  # type: ignore
                )
            except (ValueError, TypeError):
                self.rating = 0.0

        self.cover_url = str(data.get("image", ""))
        self.publisher = self._clean_text(str(data.get("publisher", "")))
        self.language = self._clean_text(str(data.get("inLanguage", "")))
        self.is_abridged = data.get("abridged", "") == "true"

    def _fetch_metadata(self, locale: str = "fr") -> dict[str, Any] | None:
        url = f"https://www.audible.{locale}/pd/{self._asin}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        try:
            with httpx.Client(
                headers=headers, follow_redirects=True, timeout=10
            ) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return None

                soup = BeautifulSoup(resp.text, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")

                for s in scripts:
                    try:
                        temp_data = json.loads(str(s.string))
                        if isinstance(temp_data, list):
                            temp_data = temp_data[0]  # type: ignore
                        if temp_data.get("@type") == "Audiobook":  # type: ignore
                            return temp_data  # type: ignore
                    except (json.JSONDecodeError, TypeError):
                        continue

        except Exception as e:
            print(f"Erreur lors du fetch : {e}")
        return None

    def __str__(self) -> str:
        authors = ", ".join(self.authors) if self.authors else "Unknown"
        narrators = ", ".join(self.narrators) if self.narrators else "Unknown"
        header = f"--- {self.title.upper()} ---"
        details = (
            f"asin: {self._asin}\n"
            f"title: {self.title}\n"
            f"authors: {authors}\n"
            f"narrators: {narrators}\n"
            f"description: {self.description}\n"
            f"release_date: {self.release_date}\n"
            f"duration: {self.duration}\n"
            f"rating: {self.rating}\n"
            f"cover_url: {self.cover_url}\n"
            f"publisher: {self.publisher}\n"
            f"language: {self.language}\n"
            f"is_abridged: {self.is_abridged}\n"
        )
        return f"\n{header}\n{details}\n{'-' * len(header)}"
