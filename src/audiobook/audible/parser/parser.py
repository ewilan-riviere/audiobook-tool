from audiobook.common import AutoRepr


class AudibleParser(AutoRepr):
    _asin: str | None = None
    url: str | None = None

    def _format_url(self, asin: str, locale: str = "com"):
        return f"https://www.audible.{locale}/pd/{asin}"

    @property
    def _cookies(self):
        # Cookies are added to “fix” the location to the US.
        return {"lc-main-av": "en_US"}

    @property
    def _headers(self):
        return {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            # "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            # "Referer": f"https://www.audible.{locale}/",
            "Referer": "https://www.google.com/",
        }
