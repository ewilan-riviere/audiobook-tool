"""Fetch Audible URL"""

import time
import random
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, Browser, Error as PlaywrightError
from playwright_stealth.stealth import Stealth  # type: ignore
from fake_useragent import UserAgent
from audiobook.common import AutoRepr


class AudibleFetch(AutoRepr):
    """Fetch Audible URL"""

    DOMAINS = ["fr", "com", "co.uk", "de"]

    def __init__(self, asin: str, locale: str | None = "com"):
        self.asin = asin
        self.locale = locale
        self.url: str | None = None
        self.soup: BeautifulSoup | None = None
        self.success: bool = False
        self.error: str | None = None

        self.ua = UserAgent(browsers=["chrome"], os=["windows"])
        self._run_fetch_loop()

    def _run_fetch_loop(self):
        max_retries = 5
        attempts = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-dev-shm-usage", "--disable-gpu"],
            )

            while attempts < max_retries and not self.success:
                target_locales = [self.locale] if self.locale else self.DOMAINS

                for loc in target_locales:
                    if self.success:
                        break
                    print(
                        f"\n[Attempt {attempts + 1}] Target: {loc} for ASIN: {self.asin}"
                    )
                    self._fetch(browser, loc, attempts)

                attempts += 1
                if not self.success and attempts < max_retries:
                    wait_time = random.uniform(1, 3)
                    print(f"[*] Waiting {wait_time:.2f}s before next retry...")
                    time.sleep(wait_time)

            browser.close()

    def _fetch(self, browser: Browser, locale: str, attempts: int):
        """Internal fetch logic"""
        url = f"https://www.audible.{locale}/pd/{self.asin}"
        if self.locale or attempts > 0:
            url = f"{url}?ipRedirectOverride=true"

        # New context
        context = browser.new_context(
            user_agent=self.ua.random,
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        stealth_config = Stealth()
        stealth_config.apply_stealth_sync(page)

        # page.on(
        #     "response", lambda res: print(f"   <- Res: {res.status} {res.url[:60]}")
        # )

        page.route(
            "**/*.{png,jpg,jpeg,gif,webp,woff,woff2,svg,css}",
            lambda route: route.abort(),
        )

        try:
            print(f"[>] Navigating to: {url}")
            response = page.goto(url, timeout=30000, wait_until="domcontentloaded")

            if not response:
                print("[!] Error: No response (Timeout or Connection Closed)")
            elif not response.ok:
                print(f"[!] HTTP Error {response.status}: {response.url}")
            else:
                final_url = response.url
                parsed_path = urlparse(final_url).path

                if parsed_path == "/" or "/pd/" not in parsed_path:
                    print(
                        f"[?] Redirected to home/login. ASIN maybe not found on .{locale}"
                    )
                else:
                    html_content = page.content()
                    print(f"[+] Success! Page size: {len(html_content)} bytes")

                    self.soup = BeautifulSoup(html_content, "html.parser")
                    self.url = final_url
                    self.success = True

                    print(f"[*] Title: {page.title()}")

        except PlaywrightError as e:
            print(f"[EXCEPT] Playwright failed: {e}")
            # page.screenshot(path="error_debug.png")

        finally:
            context.close()
