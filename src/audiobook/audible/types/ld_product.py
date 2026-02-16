"""Represents Audible JSON-LD Product"""

from dataclasses import dataclass
from .web_scraper import WebScraper


@dataclass
class LDProduct(WebScraper):
    """Represents Audible JSON-LD Product"""

    context: str | None = None
    type_: str | None = None
    additional_type: str | None = None
    product_id: str | None = None
    name: str | None = None
    image: str | None = None
    sku: str | None = None
    brand: str | None = None
    rating_value: str | None = None
    rating_count: str | None = None
    price: str | None = None
    currency: str | None = None

    @property
    def rating_value_typed(self) -> float | None:
        return self._to_float(self.rating_value)

    @property
    def rating_count_typed(self) -> int | None:
        return self._to_int(self.rating_count)

    @property
    def price_typed(self) -> float | None:
        return self._to_float(self.price)
