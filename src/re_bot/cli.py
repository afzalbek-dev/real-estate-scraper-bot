import argparse
import sys
import json
import time
from .models import PropertyListing
from .storage import PropertyStorage
from .analyzer import PropertyAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Real Estate Scraper Bot - Ko'chmas mulk narxlari tahlili")
    parser.add_argument("--db", default="/tmp/real_estate.db", help="SQLite ma'lumotlar bazasi fayli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="E'lon qo'shish yoki narxni yangilash")
    add_p.add_argument("--id", required=True)
    add_p.add_argument("--title", required=True)
    add_p.add_argument("--district", required=True)
    add_p.add_argument("--rooms", type=int, default=2)
    add_p.add_argument("--area", type=float, required=True)
    add_p.add_argument("--price", type=float, required=True)
    add_p.add_argument("--url", default="https://example.com/property")

    search_p = subparsers.add_parser("search", help="E'lonlarni qidirish")
    search_p.add_argument("--district", help="Tuman")
    search_p.add_argument("--max-price", type=float, help="Maksimal narx (USD)")
    search_p.add_argument("--min-rooms", type=int, help="Minimal xonalar soni")

    drops_p = subparsers.add_parser("price-drops", help="Narxi arzonlashgan e'lonlar")
    stats_p = subparsers.add_parser("stats", help="Tumanlar bo'yicha tahlil")

    args = parser.parse_args()
    storage = PropertyStorage(args.db)
    analyzer = PropertyAnalyzer(storage)

    if args.command == "add":
        item = PropertyListing(
            id=args.id,
            title=args.title,
            district=args.district,
            rooms=args.rooms,
            area_sqm=args.area,
            price_usd=args.price,
            url=args.url,
            created_at=time.time(),
        )
        is_new, price_change = storage.upsert_listing(item)
        if is_new:
            print(f"✅ Yangi e'lon qo'shildi: {item.title} (${item.price_usd:,.0f})")
        elif price_change:
            print(f"📉 Narx o'zgardi! {price_change.old_price} -> {price_change.new_price} ({price_change.percent_change}%)")
        else:
            print(f"E'lon yangilandi (narx o'zgarmadi): {item.id}")
    elif args.command == "search":
        items = storage.search_listings(args.district, args.max_price, args.min_rooms)
        print(f"Topilgan e'lonlar: {len(items)} ta")
        for it in items:
            print(f"#{it.id} [{it.district}] {it.rooms}-xona, {it.area_sqm} m² | ${it.price_usd:,.0f} (${it.price_per_sqm:,.0f}/m²)")
    elif args.command == "price-drops":
        drops = storage.get_recent_price_drops()
        print(f"Arzonlashgan e'lonlar ({len(drops)} ta):")
        for d in drops:
            print(f"ID: {d.listing_id} | ${d.old_price:,.0f} -> ${d.new_price:,.0f} ({d.percent_change}%)")
    elif args.command == "stats":
        print(json.dumps(analyzer.get_district_stats(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
