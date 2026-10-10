from dataclasses import dataclass
from typing import Optional


@dataclass
class PropertyListing:
    id: str
    title: str
    district: str
    rooms: int
    area_sqm: float
    price_usd: float
    url: str
    created_at: float

    @property
    def price_per_sqm(self) -> float:
        if self.area_sqm <= 0:
            return 0.0
        return round(self.price_usd / self.area_sqm, 2)


@dataclass
class PriceChange:
    listing_id: str
    old_price: float
    new_price: float
    diff: float
    percent_change: float
    timestamp: float
