from typing import Optional
import re
from datetime import datetime, date, time
from audiobook.common import AutoRepr


class AudibleAudiobook(AutoRepr):
    asin: Optional[str]
    url: Optional[str]
    fetched_at: Optional[datetime]

    title: Optional[str]
    subtitle: Optional[str]
    description: Optional[str]
    copyright: Optional[str]
    publisher: Optional[str]

    authors: Optional[list[str]]
    narrators: Optional[list[str]]

    published_at: Optional[date]
    duration: Optional[time]
    language: Optional[str]
    abridged: Optional[bool]
    cover: Optional[str]

    series: Optional[list[str]]
    series_main: Optional[str]
    part: Optional[str]
    volume: Optional[float]

    format: Optional[str]
    book_format: Optional[str]
    sku: Optional[str]

    rating: Optional[float]
    price: Optional[float]

    genres: Optional[list[str]]
    categories: Optional[list[str]]

    title_clean: Optional[str]
    series_clean: Optional[str]
    volume_clean: Optional[float]

    def __init__(self, asin: str):
        self.asin = asin
        self.fetched_at = datetime.now()

    @property
    def genres_all(self) -> list[str] | None:
        """Get genres with categories"""
        genres = self.genres
        categories = self.categories
        if not genres:
            genres = []
        if not categories:
            categories = []

        items = genres + categories

        return items

    @property
    def duration_human(self) -> str | None:
        """Get duration as human readable"""
        if not self.duration:
            return None

        return self.duration.strftime("%H:%M:%S")

    def clean(self) -> dict[str, str | float | None]:
        clean_title: str | None = None
        clean_series: str | None = None
        clean_volume: float | None = None

        # 1. Extraction du Volume (Logique renforcée)
        # On cherche d'abord les mots-clés, puis un chiffre isolé à la fin si rien n'est trouvé
        full_text = f"{self.title or ''} {self.subtitle or ''} {self.series_main or ''}"

        # Tentative A : Mot-clé + Chiffre (Tome 2, Book 1.5)
        volume_match = re.search(
            r"(?i)(?:book|tome|vol|volume|n°|livre|part|partie)\s?(\d+(?:\.\d+)?)",
            full_text,
        )

        if volume_match:
            clean_volume = float(volume_match.group(1))
        else:
            # Tentative B : Chiffre isolé à la fin du titre ou du sous-titre
            # (ex: "La croisade noire 2")
            digit_match = re.search(
                r"(\d+(?:\.\d+)?)$", (self.subtitle or self.title or "").strip()
            )
            if digit_match:
                clean_volume = float(digit_match.group(1))

        # 2. Nettoyage du Titre
        if self.title:
            # On enlève d'abord les parenthèses (souvent des infos techniques)
            t = re.sub(r"\(.*?\)", "", self.title)

            # Au lieu de split sur le tiret (qui casse Passe-Miroir),
            # on ne coupe que si le tiret est suivi d'un mot-clé de volume ou de série
            t = re.sub(
                r"(?i)\s*[:\-\u2013\u2014]\s*(?:book|tome|vol|volume|livre|part).*$",
                "",
                t,
            )

            # Si le titre contient encore un ":" ou "-" (souvent "Série - Titre"),
            # on essaie d'isoler le titre s'il y a un doublon avec series_main
            if self.series_main and (" - " in t or " : " in t):
                parts = re.split(r"\s*[:\-\u2013\u2014]\s*", t)
                # On garde la partie qui n'est pas le nom de la série
                t = next(
                    (p for p in parts if p.lower() not in self.series_main.lower()),
                    parts[0],
                )

            clean_title = t.strip()

        # 3. Nettoyage de la Série
        series_raw = self.series_main if self.series_main else self.subtitle
        if series_raw:
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
            clean_series = re.sub(
                r"(?i)\b(Novels|Trilogy|Series|Collection|Novela|Saga)\b", "", s
            ).strip()

        # Fallback sur le volume d'origine si l'extraction a échoué
        if clean_volume is None and hasattr(self, "volume") and self.volume:
            clean_volume = float(self.volume)

        return {
            "title": clean_title,
            "series": clean_series,
            "volume": clean_volume,
        }
