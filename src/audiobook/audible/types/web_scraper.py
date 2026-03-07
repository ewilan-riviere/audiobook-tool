import re
from datetime import datetime, date, timedelta
import string


class WebScraper:
    def _to_int(self, value: str | None) -> int | None:
        """Convert `str` to `int`"""
        if not value:
            return None

        return int(value)

    def _to_float(self, value: str | None) -> float | None:
        """Convert `str` to `float`"""
        if not value:
            return None

        val = float(value)
        return round(val, 2)

    def _to_bool(self, value: str | None) -> bool:
        """Convert `str` to `bool`"""
        if not value:
            return False

        return value.lower() in ("true", "1", "yes", "t")

    def _to_date(self, date_: str | None) -> date | None:
        if not date_:
            return None

        return datetime.strptime(date_, "%Y-%m-%d").date()

    def _to_seconds(self, timedelta_: timedelta | None) -> int | None:
        if not timedelta_:
            return None

        return round(timedelta_.total_seconds())

    def _to_time(self, duration_: str | None) -> timedelta | None:
        """Parse ISO 8601 to time"""
        if not duration_:
            return None

        pattern = r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?"
        match = re.match(pattern, duration_)

        if not match:
            return None

        h = int(match.group("hours") or 0)
        m = int(match.group("minutes") or 0)
        s = int(match.group("seconds") or 0)

        td = timedelta(hours=h, minutes=m, seconds=s)

        return td

    def _to_time_human(self, timedelta_: timedelta | None) -> str | None:
        """timedelta to human time"""
        if not timedelta_:
            return None

        total_seconds = int(timedelta_.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _handle_authors(self, authors: list[str] | None) -> list[str]:
        items: list[str] = []
        if not authors:
            return []

        for author in authors:
            if any(word in author for word in ["traducteur", "translator"]):
                continue
            else:
                items.append(author)

        formatted_authors = [string.capwords(name) for name in items]

        return formatted_authors
