"""Fetch Audible URL"""

import time
from typing import Any
import random
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Browser, Error as PlaywrightError
from playwright_stealth.stealth import Stealth  # type: ignore
from audiobook.audible.types import (
    AudibleHtml,
    LDAudiobook,
    LDProduct,
    JsonDuration,
    JsonRating,
    AudibleExtra,
)
from audiobook.common import AutoRepr
from .parser import ParserHtml, ParserJson


class AudibleFetch(AutoRepr):
    """Fetch Audible URL"""

    DOMAINS = ["fr", "com", "co.uk", "de"]

    def __init__(self, asin: str, locale: str | None = "com"):
        self.asin = asin
        self.locale = locale
        self.url: str | None = None
        self.success: bool = False
        self.error: str | None = None

        self.html: AudibleHtml = AudibleHtml()
        self.ld_audiobook = LDAudiobook()
        self.ld_product = LDProduct()
        self.json_duration = JsonDuration()
        self.json_rating = JsonRating()
        self.extra = AudibleExtra()

        self._run_fetch_loop()

    def _run_fetch_loop(self):
        max_retries = 5
        attempts = 0

        with sync_playwright() as p:
            desktop_devices = [  # type: ignore
                name for name, device in p.devices.items() if "Desktop" in name  # type: ignore
            ]
            random_device_name = random.choice(desktop_devices)  # type: ignore
            self.device_config: Any = p.devices[random_device_name]  # type: ignore

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

        context = browser.new_context(**self.device_config)
        page = context.new_page()

        stealth_config = Stealth()
        stealth_config.apply_stealth_sync(page)

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

                    self.html = ParserHtml(page).content
                    json_ = ParserJson(page)
                    self.ld_audiobook = json_.ld_audiobook
                    self.ld_product = json_.ld_product
                    self.json_duration = json_.json_duration
                    self.json_rating = json_.json_rating
                    self.extra = AudibleExtra(
                        scraped_series=self.json_duration.series_typed,
                        scraped_part=self.json_duration.part_typed,
                        scraped_title=self.ld_audiobook.name,
                        scraped_subtitle=self.html.subtitle,
                        scraped_genres=self.html.genres,
                        scraped_categories=self.json_duration.categories,
                    ).run()

                    self.url = final_url
                    self.success = True

                    print(f"[*] Title: {page.title()}")

        except PlaywrightError as e:
            print(f"[EXCEPT] Playwright failed: {e}")
            # page.screenshot(path="error_debug.png")

        finally:
            context.close()
