"""Fetch Audible URL"""

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from playwright_stealth import Stealth  # type: ignore
from fake_useragent import UserAgent
from audiobook.common import AutoRepr


class AudibleFetch(AutoRepr):
    """Fetch Audible URL"""

    # https://audible.readthedocs.io/en/latest/marketplaces/marketplaces.html
    DOMAINS = ["fr", "com", "co.uk", "de"]

    asin: str
    locale: str | None = "com"
    url: str | None = None
    soup: BeautifulSoup | None = None
    success: bool = False
    error: str | None = None

    def __init__(self, asin: str, locale: str | None):
        self.asin = asin
        self.locale = locale

        max_retries = 5
        attempts = 0

        while attempts < max_retries and not self.success:
            if not locale:
                for domain in self.DOMAINS:
                    self._fetch(domain, attempts)
            else:
                self._fetch(locale, attempts)
            attempts += 1
            if not self.success and attempts < max_retries:
                print(f"Attempt {attempts} failed for {asin}, new try...")
                # Optional: import time; time.sleep(1)

    def _fetch(self, locale: str, attempts: int):
        """Parse Audible to find right URL"""
        url = f"https://www.audible.{locale}/pd/{self.asin}"
        if self.locale or attempts > 0:
            url = f"{url}?ipRedirectOverride=true"
        ua = UserAgent(browsers=["chrome"], os=["windows"])
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=ua.random,
                    viewport={"width": 1920, "height": 1080},
                )
                page = context.new_page()

                stealth = Stealth()
                stealth.apply_stealth_sync(page)

                res = page.goto(url, timeout=30000, wait_until="domcontentloaded")

                if not res:
                    print("No response")
                elif not res.ok:
                    print(f"HTTP error: {res.status}")
                else:
                    parsed_url = urlparse(res.url)
                    if str(parsed_url.path) != "/":
                        self.soup = BeautifulSoup(res.text(), "html.parser")
                        self.url = str(res.url)
                        self.success = True

            except PlaywrightError as e:
                print(f"Browsing failed: {e}")
