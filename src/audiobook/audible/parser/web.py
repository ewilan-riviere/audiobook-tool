"""Parse Audible web output"""

from typing import List, Optional
import json
import re
import requests
from bs4 import BeautifulSoup
from .parser import AudibleParser


class AudibleParserWeb(AudibleParser):
    """Parse Audible web output"""

    title: str | None = None
    subtitle: str | None = None
    series_json: str | None = None
    series_web: str | None = None
    series: str | None = None
    genres: list[str] | None = []
    volume: int | None = None
    description: str | None = None
    copyright_audible: str | None = None

    def __init__(self, url: str):
        self.url = url
        self._soup: Optional[BeautifulSoup] = None
        # Creating a session to manage cookies
        self._session = requests.Session()
        self._session.headers.update(self._headers)

        self.success = self._parse_url()

        self.title = self._parse_title()
        self.subtitle = self._parse_title()
        self.series = self._parse_series()
        chips_labels = self._parse_chips_text()
        print(chips_labels)

        # if self._fetch_page():
        #     self.title = self._parse_title()
        #     self.subtitle = self._parse_subtitle()
        #     self.series_json = self._parse_series_name()
        #     self.genres = self._parse_chips_text()
        #     self._parse_description_and_copyright()

        #     if self.subtitle:
        #         self._parse_series_from_subtitle(self.subtitle)

        # self.series = self.series_web or self.series_json
        # if self.series and not self.volume:
        #     self._extract_implicit_volume()
        #     if not self.volume:
        #         self.volume = 1

    def _parse_url(self) -> bool:
        if not self.url:
            return False

        try:
            # We use the session instead of requests directly.
            res = self._session.get(self.url, timeout=15)

            if res.status_code == 503:
                print("Error 503: blocked by anti-bot (CAPTCHA)")
                return False

            res.raise_for_status()
            self._soup = BeautifulSoup(res.text, "html.parser")

            return True

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")

        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")

        return False

    def _parse_title(self) -> Optional[str]:
        """Parse title from <h1>"""
        if self._soup:
            tag = self._soup.find("h1", attrs={"slot": "title"})
            if tag:
                return tag.get_text().strip()
        return None

    def _parse_subtitle(self) -> Optional[str]:
        """Extract subtitle from the <h2>"""
        if self._soup:
            tag = self._soup.find("h2", attrs={"slot": "subtitle"})
            if tag:
                return tag.get_text().strip()
        return None

    def _parse_series(self) -> Optional[str]:
        """Extract subtitle from the <h2>"""
        if self._soup:
            tag = self._soup.find("div", attrs={"key": "series"})
            if tag:
                return tag.get_text().strip()
        return None

    def _parse_chips_text(self) -> List[str]:
        """Extract the text from all <adbl-chip>"""
        chips_labels: List[str] = []

        if self._soup:
            # We are looking for all <adbl-chip>
            tags = self._soup.find_all("adbl-chip")

            for tag in tags:
                # .get_text() retrieves the text inside the tag
                text = tag.get_text().strip()
                if text:
                    chips_labels.append(text)

        if len(chips_labels) > 0:
            chips_labels.pop()

        return chips_labels

    # def _parse_description_and_copyright(self):
    #     """Extract the description (p tags) and copyright (final text)."""
    #     if not self._soup:
    #         return

    #     desc_block = self._soup.find("adbl-text-block", attrs={"slot": "summary"})

    #     if desc_block:
    #         # Extraction of description (paragraphs)
    #         paragraphs = [p.get_text().strip() for p in desc_block.find_all("p")]
    #         self.description = "\n\n".join(paragraphs)

    #         # Copyright extraction
    #         # We retrieve the text that is not within the <p> tags.
    #         # .find_all(string=True, recursive=False) takes the text directly from the block
    #         full_text = desc_block.get_text(separator="|", strip=True)
    #         # Often the copyright notice appears after the last paragraph.
    #         parts = full_text.split("|")
    #         if parts:
    #             self.copyright_audible = parts[-1].strip()

    # def _parse_series_name(self) -> Optional[str]:
    #     if not self._soup:
    #         return None

    #     # We retrieve ALL JSON blocks from the page.
    #     all_json_scripts = self._soup.find_all("script", type="application/json")

    #     for script in all_json_scripts:
    #         content = script.string
    #         if (
    #             content and '"series"' in content
    #         ):  # We check whether this JSON refers to series.
    #             try:
    #                 data = json.loads(content)
    #                 series_list = data.get("series", [])
    #                 if series_list:
    #                     # Return the name of the first series found
    #                     return series_list[0].get("name")
    #             except (json.JSONDecodeError, KeyError, IndexError):
    #                 continue  # If there is an error on this block, move on to the next one.

    #     return None

    # def _parse_series_from_subtitle(self, subtitle: str):
    #     pattern = r"^(.*?)[, \-]+(?:Book|Tome)?\s*(\d+)$"
    #     match = re.search(pattern, subtitle)
    #     if match:
    #         serie = match.group(1).strip()
    #         serie = serie.replace(", Vol.", "")
    #         volume = match.group(2)

    #         self.series_web = serie
    #         self.volume = int(volume)
    #     else:
    #         print(f"Unknown format : {subtitle}")

    # def _extract_implicit_volume(self):
    #     if not self.title:
    #         return None

    #     # \d+ search for one or more consecutive digits
    #     match = re.search(r"\d+", self.title)

    #     if match:
    #         self.volume = int(match.group())
