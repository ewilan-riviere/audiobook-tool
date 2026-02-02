"""Parse Audible web output"""

from typing import List, Optional
import json
import re
import requests
from bs4 import BeautifulSoup


class AudibleParser:
    """Parse Audible web output"""

    def __init__(self, url: str):
        self._url: str = url
        self._soup: Optional[BeautifulSoup] = None
        # Création d'une session pour gérer les cookies
        self._session = requests.Session()
        # Headers plus complets (User-Agent + Accept-Language)
        self._session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.google.com/",
            }
        )

        self.title: str | None = None
        self.subtitle: str | None = None
        self.series_json: str | None = None
        self.series_web: str | None = None
        self.series: str | None = None
        self.genres: list[str] | None = []
        self.volume: int | None = None
        self.description: str | None = None
        self.copyright: str | None = None

        if self._fetch_page():
            self.title = self._parse_title()
            self.subtitle = self._parse_subtitle()
            self.series_json = self._parse_series_name()
            self.genres = self._parse_chips_text()
            self._parse_description_and_copyright()

            if self.subtitle:
                self._parse_series_from_subtitle(self.subtitle)

        self.series = self.series_web or self.series_json
        if self.series and not self.volume:
            self._extract_implicit_volume()
            if not self.volume:
                self.volume = 1

    def _fetch_page(self) -> bool:
        try:
            # On utilise la session au lieu de requests directement
            response = self._session.get(self._url, timeout=15)

            if response.status_code == 503:
                print("Error 503: blocked by anti-bot (CAPTCHA)")
                return False

            response.raise_for_status()
            self._soup = BeautifulSoup(response.text, "html.parser")
            return True

        except requests.exceptions.HTTPError as e:
            print(f"Erreur HTTP : {e}")
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion : {e}")
        return False

    def _parse_title(self) -> Optional[str]:
        """Exemple spécifique pour Audible (balise h1)"""
        if self._soup:
            title_tag = self._soup.find("h1")
            return title_tag.get_text().strip() if title_tag else None
        return None

    def _parse_subtitle(self) -> Optional[str]:
        """Extrait le texte du <h2> ayant l'attribut slot='subtitle'."""
        if self._soup:
            # On cherche la balise h2 avec le dictionnaire d'attributs
            subtitle_tag = self._soup.find("h2", attrs={"slot": "subtitle"})

            if subtitle_tag:
                return subtitle_tag.get_text().strip()
        return None

    def _parse_description_and_copyright(self):
        """Extrait la description (balises p) et le copyright (texte final)."""
        if not self._soup:
            return

        # On cible le bloc spécifique
        desc_block = self._soup.find("adbl-text-block", attrs={"slot": "summary"})

        if desc_block:
            # 1. Extraction de la description (paragraphes)
            paragraphs = [p.get_text().strip() for p in desc_block.find_all("p")]
            self.description = "\n\n".join(paragraphs)

            # 2. Extraction du copyright
            # On récupère le texte qui n'est pas dans les balises <p>
            # .find_all(string=True, recursive=False) prend le texte direct du bloc
            full_text = desc_block.get_text(separator="|", strip=True)
            # Souvent le copyright est après le dernier paragraphe
            parts = full_text.split("|")
            if parts:
                self.copyright = parts[-1].strip()

    def _parse_chips_text(self) -> List[str]:
        """Extrait le texte de tous les éléments <adbl-chip>."""
        chips_labels: List[str] = []

        if self._soup:
            # On cherche tous les éléments <adbl-chip>
            # BeautifulSoup gère très bien les balises personnalisées
            tags = self._soup.find_all("adbl-chip")

            for tag in tags:
                # .get_text() récupère le texte à l'intérieur de la balise
                text = tag.get_text().strip()
                if text:
                    chips_labels.append(text)

        if len(chips_labels) > 0:
            chips_labels.pop()

        return chips_labels

    def _parse_series_name(self) -> Optional[str]:
        if not self._soup:
            return None

        # 1. On récupère TOUS les blocs JSON de la page
        all_json_scripts = self._soup.find_all("script", type="application/json")

        for script in all_json_scripts:
            content = script.string
            if (
                content and '"series"' in content
            ):  # On vérifie si ce JSON parle de séries
                try:
                    data = json.loads(content)
                    series_list = data.get("series", [])
                    if series_list:
                        # On retourne le nom de la première série trouvée
                        return series_list[0].get("name")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue  # Si erreur sur ce bloc, on passe au suivant

        return None

    def _parse_series_from_subtitle(self, subtitle: str):
        pattern = r"^(.*?)[, \-]+(?:Book|Tome)?\s*(\d+)$"
        match = re.search(pattern, subtitle)
        if match:
            serie = match.group(1).strip()
            serie = serie.replace(", Vol.", "")
            volume = match.group(2)

            self.series_web = serie
            self.volume = int(volume)
        else:
            print(f"Unknown format : {subtitle}")

    def _extract_implicit_volume(self):
        if not self.title:
            return None

        # \d+ cherche un ou plusieurs chiffres consécutifs
        match = re.search(r"\d+", self.title)

        if match:
            self.volume = int(match.group())

    def __str__(self) -> str:
        details = (
            f"title: {self.title}\n"
            f"subtitle: {self.subtitle}\n"
            f"series: {self.series}\n"
            f"series_json: {self.series_json}\n"
            f"series_web: {self.series_web}\n"
            f"genres: {self.genres}\n"
            f"volume: {self.volume}\n"
            f"description: {self.description}\n"
            f"copyright: {self.copyright}\n"
        )
        return f"{details}"
