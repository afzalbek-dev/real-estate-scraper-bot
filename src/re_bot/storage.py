import sqlite3
import time
from typing import Optional, List, Dict, Any, Tuple
from .models import PropertyListing, PriceChange


class PropertyStorage:
    """E'lonlar va narxlar tarixini SQLite bazasida saqlash."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._init_db()

    def _init_db(self):
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    district TEXT NOT NULL,
                    rooms INTEGER NOT NULL,
                    area_sqm REAL NOT NULL,
                    price_usd REAL NOT NULL,
                    url TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    listing_id TEXT NOT NULL,
                    old_price REAL NOT NULL,
                    new_price REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY(listing_id) REFERENCES listings(id)
                )
                """
            )

    def upsert_listing(self, listing: PropertyListing) -> Tuple[bool, Optional[PriceChange]]:
        cur = self._conn.cursor()
        cur.execute("SELECT price_usd FROM listings WHERE id = ?", (listing.id,))
        existing = cur.fetchone()

        price_change = None
        now = time.time()

        with self._conn:
            if existing:
                old_price = existing[0]
                if old_price != listing.price_usd:
                    diff = listing.price_usd - old_price
                    pct = round((diff / old_price) * 100, 2) if old_price > 0 else 0.0
                    price_change = PriceChange(listing.id, old_price, listing.price_usd, diff, pct, now)
                    self._conn.execute(
                        "INSERT INTO price_history (listing_id, old_price, new_price, timestamp) VALUES (?, ?, ?, ?)",
                        (listing.id, old_price, listing.price_usd, now),
                    )
                    self._conn.execute(
                        "UPDATE listings SET price_usd = ?, title = ?, district = ?, rooms = ?, area_sqm = ? WHERE id = ?",
                        (listing.price_usd, listing.title, listing.district, listing.rooms, listing.area_sqm, listing.id),
                    )
                return False, price_change
            else:
                self._conn.execute(
                    """
                    INSERT INTO listings (id, title, district, rooms, area_sqm, price_usd, url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        listing.id,
                        listing.title,
                        listing.district,
                        listing.rooms,
                        listing.area_sqm,
                        listing.price_usd,
                        listing.url,
                        listing.created_at,
                    ),
                )
                return True, None

    def search_listings(
        self,
        district: Optional[str] = None,
        max_price: Optional[float] = None,
        min_rooms: Optional[int] = None,
    ) -> List[PropertyListing]:
        cur = self._conn.cursor()
        sql = "SELECT id, title, district, rooms, area_sqm, price_usd, url, created_at FROM listings WHERE 1=1"
        params = []
        if district:
            sql += " AND district LIKE ?"
            params.append(f"%{district}%")
        if max_price is not None:
            sql += " AND price_usd <= ?"
            params.append(max_price)
        if min_rooms is not None:
            sql += " AND rooms >= ?"
            params.append(min_rooms)

        sql += " ORDER BY price_usd ASC"
        cur.execute(sql, params)
        return [PropertyListing(*r) for r in cur.fetchall()]

    def get_recent_price_drops(self, limit: int = 10) -> List[PriceChange]:
        cur = self._conn.cursor()
        cur.execute(
            """
            SELECT listing_id, old_price, new_price, (new_price - old_price) as diff,
                   ROUND(((new_price - old_price) / old_price) * 100, 2) as pct, timestamp
            FROM price_history
            WHERE new_price < old_price
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [PriceChange(*r) for r in cur.fetchall()]

    def close(self):
        self._conn.close()
