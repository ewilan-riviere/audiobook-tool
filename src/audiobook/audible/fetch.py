import httpx
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from audiobook.common import AutoRepr


class AudibleFetch(AutoRepr):
    # https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html
    domains: list[str] = ["fr", "com", "co.uk", "de"]
    asin: str
    url: str | None
    soup: BeautifulSoup | None
    success: bool = False
    _headers = {}
    _cookies = {}
    error: str | None = None

    def __init__(self, asin: str):
        self.asin = asin
        self._set_headers()

        max_retries = 5
        attempts = 0

        while attempts < max_retries and not self.success:
            for domain in self.domains:
                self._fetch_session(domain)
            attempts += 1
            if not self.success and attempts < max_retries:
                print(f"Attempt {attempts} failed for {asin}, new try...")
                # Optional: import time; time.sleep(1)

    def _set_headers(self):
        language = "en-US,en;q=0.9"
        # referer = f"https://www.audible.{locale}/"
        referer = "https://www.google.com/"
        self._headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": language,
            "Referer": referer,
        }
        self._cookies = {"lc-main-av": "en_US"}

    def _fetch(self, locale: str = "com") -> bool:
        """Parse Audible to find right URL"""
        url = f"https://www.audible.{locale}/pd/{self.asin}"

        try:
            with httpx.Client(
                headers=self._headers,
                cookies=self._cookies,
                follow_redirects=True,
                timeout=15,
            ) as client:
                res = client.get(url)
                if str(res.url.path) != "/":
                    self.soup = BeautifulSoup(res.text, "html.parser")
                    self.url = str(res.url)
                    self.success = True

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error: {e}")

        return self.success

    def _fetch_session(self, locale: str = "com") -> str | None:
        """Parse Audible to find right URL"""
        url = f"https://www.audible.{locale}/pd/{self.asin}"

        try:
            _session = requests.Session()
            _session.headers.update(self._headers)
            _session.cookies.update(self._cookies)  # type: ignore
            res = _session.get(url, timeout=15)

            if res.status_code == 503:
                print("Error 503: blocked by anti-bot (CAPTCHA)")
                return None

            res.raise_for_status()

            parsed_url = urlparse(res.url)
            if str(parsed_url.path) != "/":
                self.soup = BeautifulSoup(res.text, "html.parser")
                self.url = str(res.url)
                self.success = True

            return res.text

        except requests.exceptions.HTTPError as e:
            self.error = f"HTTP error: {e}"

        except requests.exceptions.RequestException as e:
            self.error = f"Connection error: {e}"

        return None
