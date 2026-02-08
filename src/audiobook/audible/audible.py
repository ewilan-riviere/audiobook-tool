from audiobook.common import AutoRepr
from .parser import ParserJson, ParserHtml
from .audiobook import AudibleAudiobook
from .fetch import AudibleFetch


class Audible(AutoRepr):
    asin: str
    audiobook: AudibleAudiobook | None

    def __init__(self, asin: str):
        self.asin = asin
        fetch = AudibleFetch(self.asin)
        if not fetch.soup or not fetch.url:
            return

        web = ParserHtml(fetch.soup)
        json = ParserJson(fetch.soup)

        print("web.html")
        print(web.html)
        print()
        print("json.audiobook")
        print(json.audiobook)
        print()
        print("json.ld_audiobook")
        print(json.ld_audiobook)
        print()
        print("json.ld_product")
        print(json.ld_product)
        print()

        self.audiobook = AudibleAudiobook(self.asin, fetch.url)

        self.audiobook.title = web.html["title"]
        self.audiobook.subtitle = web.html["subtitle"]
        self.audiobook.description = web.html["description"]
        self.audiobook.copyright = web.html["copyright"]
        self.audiobook.publisher = json.ld_audiobook["publisher"]

        self.audiobook.authors = json.audiobook["authors"]
        self.audiobook.narrators = json.audiobook["narrators"]

        self.audiobook.published_at = json.ld_audiobook["date_published"]
        self.audiobook.duration = json.ld_audiobook["duration"]
        self.audiobook.language = json.ld_audiobook["in_language"]
        self.audiobook.abridged = json.ld_audiobook["abridged"]
        self.audiobook.cover = json.ld_audiobook["image"]

        self.audiobook.series = json.audiobook["series"]
        self.audiobook.volume = 1

        self.audiobook.format = json.audiobook["format"]
        self.audiobook.book_format = json.ld_audiobook["book_format"]
        self.audiobook.sku = json.ld_product["sku"]

        self.audiobook.rating = json.audiobook["rating"]
        self.audiobook.price = json.ld_audiobook["price"]

        self.audiobook.genres = web.html["genres"]
        self.audiobook.categories = json.audiobook["categories"]

        print(self.audiobook)

    # def _parse_series_from_subtitle(self, subtitle: str):
    #     pattern = r"^(.*?)[, \-]+(?:Book|Tome|Volume)?\s*(\d+)$"
    #     match = re.search(pattern, subtitle)
    #     if match:
    #         serie = match.group(1).strip()
    #         serie = serie.replace(", Vol.", "")
    #         volume = match.group(2)

    #         self.series_web = serie
    #         self.volume = int(volume)
    #     else:
    #         print(f"Unknown format : {subtitle}")

    # def _parse_implicit_volume(self):
    #     if not self.title:
    #         return None

    #     # \d+ search for one or more consecutive digits
    #     match = re.search(r"\d+", self.title)

    #     if match:
    #         self.volume = int(match.group())

    # def _extract_duration_human(self, data: Dict[str, Any]) -> str | None:
    #     """Parse ISO 8601 to human duration"""
    #     iso_duration = self._extract(data, "duration")
    #     if not iso_duration:
    #         return None

    #     return (
    #         iso_duration.replace("PT", "").replace("H", "h ").replace("M", "m").strip()
    #     )

    # def _clean(self, text: str) -> str:
    #     """Clean text"""
    #     if not text:
    #         return ""

    #     # Replace paragraph breaks with line breaks
    #     text = re.sub(r"</p>|<br\s*/?>|</div>", "\n", text)

    #     # Remove all other HTML tags
    #     clean = re.compile("<.*?>")
    #     text = re.sub(clean, "", text)

    #     # Unescape, strip, and clean up unnecessary empty lines
    #     text = html.unescape(text).strip()

    #     # Optional: avoid having 4 line breaks if the HTML was complex
    #     return "\n".join(line.strip() for line in text.splitlines() if line.strip())
