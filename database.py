import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

DB = Path(__file__).parent / "prices.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def create_db() -> None:
    conn = connect()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            brand TEXT,
            model TEXT,
            target_min REAL,
            target_max REAL NOT NULL,
            required_keywords TEXT NOT NULL DEFAULT '[]',
            blocked_keywords TEXT NOT NULL DEFAULT '[]',
            priority TEXT NOT NULL DEFAULT 'media',
            sources TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            store TEXT,
            source TEXT NOT NULL,
            url TEXT,
            score REAL NOT NULL DEFAULT 0,
            captured_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            offer_id INTEGER,
            reason TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id),
            FOREIGN KEY(offer_id) REFERENCES offers(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            date TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_prices_product_date ON prices(product, date)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_offers_product_date ON offers(product_id, captured_at)"
    )
    conn.commit()
    conn.close()


def _json_dump(value: Any) -> str:
    return json.dumps(value or [], ensure_ascii=False)


def upsert_product(item: dict) -> int:
    now = datetime.now().isoformat()
    price_range = item.get("target_price_range") or {}
    target_max = item.get("target_price", price_range.get("max"))
    if target_max is None:
        raise ValueError(f"Produto sem target_price_range.max: {item.get('name')}")

    conn = connect()
    conn.execute(
        """
        INSERT INTO products (
            name, brand, model, target_min, target_max, required_keywords,
            blocked_keywords, priority, sources, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            brand = excluded.brand,
            model = excluded.model,
            target_min = excluded.target_min,
            target_max = excluded.target_max,
            required_keywords = excluded.required_keywords,
            blocked_keywords = excluded.blocked_keywords,
            priority = excluded.priority,
            sources = excluded.sources,
            status = excluded.status,
            updated_at = excluded.updated_at
        """,
        (
            item["name"],
            item.get("brand"),
            item.get("model"),
            price_range.get("min"),
            target_max,
            _json_dump(item.get("required_keywords")),
            _json_dump(item.get("blocked_keywords")),
            item.get("priority", "media"),
            _json_dump(item.get("sources")),
            item.get("status", "active"),
            now,
            now,
        ),
    )
    row = conn.execute("SELECT id FROM products WHERE name = ?", (item["name"],)).fetchone()
    conn.commit()
    conn.close()
    return int(row["id"])


def save_price(product: str, value: float) -> None:
    conn = connect()
    conn.execute(
        "INSERT INTO prices (product, price, date) VALUES (?, ?, ?)",
        (product, value, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def save_offer(
    product_name: str,
    title: str,
    price: float,
    source: str,
    *,
    store: str | None = None,
    url: str | None = None,
    score: float = 0,
) -> int:
    conn = connect()
    row = conn.execute(
        "SELECT id FROM products WHERE name = ?",
        (product_name,),
    ).fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"Produto nao cadastrado no SQLite: {product_name}")

    cursor = conn.execute(
        """
        INSERT INTO offers (product_id, title, price, store, source, url, score, captured_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            row["id"],
            title,
            price,
            store,
            source,
            url,
            score,
            datetime.now().isoformat(),
        ),
    )
    conn.commit()
    offer_id = int(cursor.lastrowid)
    conn.close()
    save_price(product_name, price)
    return offer_id


def save_alert(product_name: str, reason: str, message: str, offer_id: int | None = None) -> int:
    conn = connect()
    row = conn.execute(
        "SELECT id FROM products WHERE name = ?",
        (product_name,),
    ).fetchone()
    if row is None:
        conn.close()
        raise ValueError(f"Produto nao cadastrado no SQLite: {product_name}")

    cursor = conn.execute(
        """
        INSERT INTO alerts (product_id, offer_id, reason, message, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (row["id"], offer_id, reason, message, datetime.now().isoformat()),
    )
    conn.commit()
    alert_id = int(cursor.lastrowid)
    conn.close()
    return alert_id


def get_last_price(product: str) -> float | None:
    conn = connect()
    row = conn.execute(
        """
        SELECT price FROM prices
        WHERE product = ?
        ORDER BY date DESC
        LIMIT 1
        """,
        (product,),
    ).fetchone()
    conn.close()
    return row["price"] if row else None


def get_min_price_days(product: str, days: int = 30) -> float | None:
    since = (datetime.now() - timedelta(days=days)).isoformat()
    conn = connect()
    row = conn.execute(
        """
        SELECT MIN(price) AS value FROM prices
        WHERE product = ? AND date >= ?
        """,
        (product, since),
    ).fetchone()
    conn.close()
    return row["value"] if row and row["value"] is not None else None


def get_price_stats(product: str, days: int = 30) -> dict[str, float | int | None]:
    since = (datetime.now() - timedelta(days=days)).isoformat()
    conn = connect()
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS samples,
            MIN(price) AS minimum,
            AVG(price) AS average,
            MAX(price) AS maximum
        FROM prices
        WHERE product = ? AND date >= ?
        """,
        (product, since),
    ).fetchone()
    conn.close()
    return {
        "samples": row["samples"] if row else 0,
        "minimum": row["minimum"] if row else None,
        "average": row["average"] if row else None,
        "maximum": row["maximum"] if row else None,
    }
