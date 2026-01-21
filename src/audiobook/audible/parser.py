from typing import List, Optional
import json
import re
import requests
from bs4 import BeautifulSoup


class AudibleParser:
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
        self.series_name: str | None = None
        self.series_name_alt: str | None = None
        self.genres: list[str] | None = []
        self.volume: int | None = None

        if self._fetch_page():
            self.title = self._parse_title()
            self.subtitle = self._parse_subtitle()
            self.series_name = self._parse_series_name()
            self.genres = self._parse_chips_text()

            if self.subtitle:
                self._parse_series_from_subtitle(self.subtitle)

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

            self.series_name_alt = serie
            self.volume = int(volume)
        else:
            print(f"Unknown format : {subtitle}")

    def __str__(self) -> str:
        details = (
            f"title: {self.title}\n"
            f"subtitle: {self.subtitle}\n"
            f"series_name: {self.series_name}\n"
            f"series_name_alt: {self.series_name_alt}\n"
            f"genres: {self.genres}\n"
            f"volume: {self.volume}\n"
        )
        return f"{details}"
