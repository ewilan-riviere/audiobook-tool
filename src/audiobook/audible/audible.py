import httpx
from bs4 import BeautifulSoup, Tag
from audiobook.common import AutoRepr
from .parser import ParserJsonld, ParserWeb
from .parser.typed import AudibleAudiobook


class Audible(AutoRepr):
    asin: str
    url: str
    audiobook: AudibleAudiobook | None

    def __init__(self, asin: str):
        self.asin = asin
        # success = self._handle()

        max_retries = 5
        attempts = 0
        success = False

        while attempts < max_retries and not success:
            self.audiobook = self._handle()
            success = self.audiobook.success
            attempts += 1
            if not success and attempts < max_retries:
                print(f"Tentative {attempts} échouée pour {asin}, nouvel essai...")
                # Optionnel: import time; time.sleep(1)

        print(self.audiobook)

    def _handle(self) -> AudibleAudiobook:
        tags = self._handle_urls(["fr", "com", "co.uk", "de"])
        parser_jsonld = ParserJsonld(tags)
        parser_web = ParserWeb(self.url)
        audiobook = AudibleAudiobook(self.asin, self.url)

        jsonld = parser_jsonld.jsonld
        html = parser_web.html
        json = parser_web.json
        if jsonld and html and json:
            audiobook.success = True
            audiobook.title = jsonld["title"]
            audiobook.description = jsonld["description"]
            audiobook.authors = jsonld["authors"]
            audiobook.narrators = jsonld["narrators"]
            audiobook.release_date = jsonld["release_date"]
            audiobook.duration_time = jsonld["duration_time"]
            audiobook.duration_human = jsonld["duration_human"]
            audiobook.rating = jsonld["rating"]
            audiobook.cover = jsonld["cover_url"]
            audiobook.publisher = jsonld["publisher"]
            audiobook.language = jsonld["language"]
            if jsonld["is_abridged"]:
                audiobook.is_abridged = jsonld["is_abridged"]

            audiobook.subtitle = html["subtitle"]
            audiobook.copyright = html["copyright"]
            audiobook.genres = html["genres"]

            audiobook.series = json["series"]
            audiobook.format = json["format"]
            audiobook.categories = json["categories"]

        return audiobook

    def _handle_urls(
        self,
        listing: list[str],
    ) -> list[Tag]:
        tags: list[Tag] = []
        # https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html
        for suffix in listing:
            items = self._parse_url(suffix)
            if items:
                tags = items

        return tags

    def _parse_url(self, locale: str = "com") -> list[Tag] | None:
        """Parse Audible to find right URL"""
        url = f"https://www.audible.{locale}/pd/{self.asin}"
        language = "en-US,en;q=0.9"
        # referer = f"https://www.audible.{locale}/"
        referer = "https://www.google.com/"

        try:
            with httpx.Client(
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": language,
                    "Referer": referer,
                },
                cookies={"lc-main-av": "en_US"},
                follow_redirects=True,
                timeout=15,
            ) as client:
                res = client.get(url)
                soup = BeautifulSoup(res.text, "html.parser")
                scripts = soup.find_all("script", type="application/ld+json")

                if len(scripts) > 1:
                    self.url = url

                    return scripts  # type: ignore

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error: {e}")

        return None
