# Real Estate Scraper Bot

Ko'chmas mulk e'lonlarini to'plash, tumanlar kesimida o'rtacha m² narxlarini tahlil qilish va narxi pasaygan (price drops) takliflarni avtomatik aniqlovchi monitoring tizimi.

## Xususiyatlari
- **Narxlar Dinamikasi & Tarixi**: Har bir e'lonning narx o'zgarishini SQLite bazasida kuzatish va arzonlashgan e'lonlar haqida ogohlantirish.
- **Kvadrat Metr Tahlili**: Har bir uyning 1 m² maydoni uchun narxini hisoblash va tumanlar bo'yicha solishtirish.
- **Qidiruv Filtrlari**: Tuman, xonalar soni va maksimal byudjet bo'yicha tezkor saralash.
- **CLI Boshqaruvi**: E'lonlarni yangilash, bozor statistikasini olish va o'zgarishlarni monitoring qilish.

## Foydalanish (Python)
```python
from re_bot import PropertyStorage, PropertyListing, PropertyAnalyzer
import time

storage = PropertyStorage("real_estate.db")
analyzer = PropertyAnalyzer(storage)

# E'lon kiritish
listing = PropertyListing(
    id="kv_105",
    title="Mirzo Ulug'bek 2-xona",
    district="Mirzo Ulug'bek",
    rooms=2,
    area_sqm=60.0,
    price_usd=55000.0,
    url="https://olx.uz/...",
    created_at=time.time(),
)
storage.upsert_listing(listing)

# Tumanlar bo'yicha tahlil
print(analyzer.get_district_stats())
```

## CLI
```bash
re-bot search --district "Yunusobod" --max-price 60000
re-bot price-drops
re-bot stats
```

## Testlar
```bash
pytest tests/ -v
```

## Litsenziya
MIT
