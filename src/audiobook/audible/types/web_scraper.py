import re
from datetime import datetime, date, time


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

    def _to_seconds(self, time_: time | None) -> int | None:
        if not time_:
            return None

        s_h = time_.hour * 3600
        s_min = time_.minute * 60
        s_s = time_.second
        s_ms = int(time_.microsecond / 1000000)

        return s_h + s_min + s_s + s_ms

    def _to_time(self, duration_: str | None) -> time | None:
        """Parse ISO 8601 to time"""
        if not duration_:
            return None

        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration_)

        if not match:
            return None

        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)

        return time(hour=h, minute=m)

    def _handle_authors(self, authors: list[str] | None) -> list[str]:
        items: list[str] = []
        if not authors:
            return []

        for author in authors:
            if any(word in author for word in ["traducteur", "translator"]):
                continue
            else:
                items.append(author)

        return items
