from typing import TypedDict, Optional


class JsonLdProduct(TypedDict):
    context: Optional[str]
    type: Optional[str]
    additional_type: Optional[str]
    product_id: Optional[str]
    name: Optional[str]
    image: Optional[str]
    sku: Optional[str]
    brand: Optional[str]
    rating: Optional[float]
    price: Optional[float]
