from typing import List, Dict, Any
from .models import PropertyListing
from .storage import PropertyStorage


class PropertyAnalyzer:
    """Ko'chmas mulk narxlari va o'rtacha kvadrat metr qiymatlarini tahlil qilish."""

    def __init__(self, storage: PropertyStorage):
        self.storage = storage

    def get_district_stats(self) -> Dict[str, Dict[str, float]]:
        listings = self.storage.search_listings()
        districts: Dict[str, List[PropertyListing]] = {}
        for item in listings:
            districts.setdefault(item.district, []).append(item)

        stats = {}
        for dist, items in districts.items():
            avg_price = sum(it.price_usd for it in items) / len(items)
            avg_sqm = sum(it.price_per_sqm for it in items) / len(items)
            stats[dist] = {
                "count": len(items),
                "avg_price_usd": round(avg_price, 2),
                "avg_price_per_sqm": round(avg_sqm, 2),
            }

        return stats
