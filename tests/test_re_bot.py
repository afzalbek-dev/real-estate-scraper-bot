import pytest
import time
from re_bot.models import PropertyListing
from re_bot.storage import PropertyStorage
from re_bot.analyzer import PropertyAnalyzer


def test_property_upsert_and_price_drop(tmp_path):
    db_file = str(tmp_path / "re_test.db")
    storage = PropertyStorage(db_file)
    analyzer = PropertyAnalyzer(storage)

    prop = PropertyListing(
        id="olx_101",
        title="Yunusobod 3-xona kvartira",
        district="Yunusobod",
        rooms=3,
        area_sqm=75.0,
        price_usd=70000.0,
        url="https://olx.uz/101",
        created_at=time.time(),
    )
    assert prop.price_per_sqm == round(70000.0 / 75.0, 2)

    # 1. Yangi qo'shish
    is_new, change = storage.upsert_listing(prop)
    assert is_new is True
    assert change is None

    # 2. Narx arzonlashishi: 70,000 -> 65,000 USD
    prop_updated = PropertyListing(
        id="olx_101",
        title="Yunusobod 3-xona kvartira",
        district="Yunusobod",
        rooms=3,
        area_sqm=75.0,
        price_usd=65000.0,
        url="https://olx.uz/101",
        created_at=time.time(),
    )
    is_new2, change2 = storage.upsert_listing(prop_updated)
    assert is_new2 is False
    assert change2 is not None
    assert change2.old_price == 70000.0
    assert change2.new_price == 65000.0
    assert change2.diff == -5000.0
    assert change2.percent_change < 0

    # 3. Arzonlashgan e'lonlar ro'yxati
    drops = storage.get_recent_price_drops()
    assert len(drops) == 1
    assert drops[0].listing_id == "olx_101"

    # 4. Tahlil
    stats = analyzer.get_district_stats()
    assert "Yunusobod" in stats
    assert stats["Yunusobod"]["count"] == 1
    assert stats["Yunusobod"]["avg_price_usd"] == 65000.0
    storage.close()


def test_search_filter():
    storage = PropertyStorage(":memory:")
    storage.upsert_listing(PropertyListing("1", "Chilonzor 2-xona", "Chilonzor", 2, 50.0, 45000.0, "url", time.time()))
    storage.upsert_listing(PropertyListing("2", "Mirobod 4-xona", "Mirobod", 4, 120.0, 150000.0, "url", time.time()))

    # Max price 50000
    res = storage.search_listings(max_price=50000.0)
    assert len(res) == 1
    assert res[0].id == "1"
