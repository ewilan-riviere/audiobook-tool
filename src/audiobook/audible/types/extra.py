"""Represents Audible extra data"""

from dataclasses import dataclass, field
import re
from .web_scraper import WebScraper


@dataclass
class AudibleExtra(WebScraper):
    """Represents Audible extra data"""

    scraped_series: str | None = None
    scraped_part: int | None = None
    scraped_title: str | None = None
    scraped_subtitle: str | None = None
    scraped_genres: list[str] | None = None
    scraped_categories: list[str] | None = None
    # post_init
    series_typed: str | None = field(init=False)
    volume_typed: float | None = field(init=False)
    title_typed: str | None = field(init=False)
    genres_typed: list[str] | None = field(init=False, default_factory=list[str])

    def __post_init__(self):
        self.volume_typed = self._clean_volume()
        self.title_typed = self._clean_title()
        self.series_typed = self._clean_series()

        genres = self.scraped_genres or []
        categories = self.scraped_categories or []
        self.genres_typed = genres + categories

    @property
    def volume_int_typed(self) -> int | None:
        if not self.volume_typed:
            return None

        return int(self.volume_typed)

    def _clean_series(self):
        series_raw = str(self.scraped_series)
        series = self.scraped_series if self.scraped_series else self.scraped_subtitle

        if not series:
            return None

        # On retire les numéros de tome qui traînent à la fin
        s = re.sub(
            r"(?i)\s*[,:\-]?\s*(?:book|tome|vol|volume|livre|part)?\s*\d+.*$",
            "",
            series_raw,
        )

        # Gestion des préfixes d'univers (ex: Star Wars - La croisade...)
        # On split et on prend la partie la plus longue pour éviter les préfixes courts
        if " - " in s or " : " in s:
            parts = re.split(r"[:\-\u2013\u2014]", s)
            s = max(parts, key=len).strip()

        # Nettoyage des suffixes de type de collection
        return re.sub(
            r"(?i)\b(Novels|Trilogy|Series|Collection|Novela|Saga)\b", "", s
        ).strip()

    def _clean_title(self):
        if not self.scraped_title:
            return None

        # On enlève d'abord les parenthèses (souvent des infos techniques)
        t = re.sub(r"\(.*?\)", "", self.scraped_title)

        # Au lieu de split sur le tiret (qui casse Passe-Miroir),
        # on ne coupe que si le tiret est suivi d'un mot-clé de volume ou de série
        t = re.sub(
            r"(?i)\s*[:\-\u2013\u2014]\s*(?:book|tome|vol|volume|livre|part).*$",
            "",
            t,
        )

        # Si le titre contient encore un ":" ou "-" (souvent "Série - Titre"),
        # on essaie d'isoler le titre s'il y a un doublon avec series_main
        if self.scraped_series and (" - " in t or " : " in t):
            parts = re.split(r"\s*[:\-\u2013\u2014]\s*", t)
            # On garde la partie qui n'est pas le nom de la série
            t = next(
                (p for p in parts if p.lower() not in self.scraped_series.lower()),
                parts[0],
            )

        return str(t).strip()

    def _clean_volume(self):
        parsed_volume = None
        # 1. Extraction du Volume (Logique renforcée)
        # On cherche d'abord les mots-clés, puis un chiffre isolé à la fin si rien n'est trouvé
        full_text = f"{self.scraped_title or ''} {self.scraped_subtitle or ''} {self.scraped_series or ''}"

        # Tentative A : Mot-clé + Chiffre (Tome 2, Book 1.5)
        volume_match = re.search(
            r"(?i)(?:book|tome|vol|volume|n°|livre|part|partie)\s?(\d+(?:\.\d+)?)",
            full_text,
        )

        if volume_match:
            parsed_volume = float(volume_match.group(1))
        else:
            # Tentative B : Chiffre isolé à la fin du titre ou du sous-titre
            # (ex: "La croisade noire 2")
            digit_match = re.search(
                r"(\d+(?:\.\d+)?)$",
                (self.scraped_subtitle or self.scraped_title or "").strip(),
            )
            if digit_match:
                parsed_volume = float(digit_match.group(1))

        # Fallback sur le volume d'origine si l'extraction a échoué
        if parsed_volume is None and hasattr(self, "volume") and self.scraped_part:
            parsed_volume = float(self.scraped_part)

        return parsed_volume
