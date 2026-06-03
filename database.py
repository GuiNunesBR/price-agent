import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB = Path(__file__).parent / "prices.db"


def create_db() -> None:
    conn = sqlite3.connect(DB)
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
    conn.commit()
    conn.close()


def save_price(product: str, value: float) -> None:
    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO prices (product, price, date) VALUES (?, ?, ?)",
        (product, value, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_last_price(product: str) -> float | None:
    conn = sqlite3.connect(DB)
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
    return row[0] if row else None


def get_min_price_days(product: str, days: int = 30) -> float | None:
    since = (datetime.now() - timedelta(days=days)).isoformat()
    conn = sqlite3.connect(DB)
    row = conn.execute(
        """
        SELECT MIN(price) FROM prices
        WHERE product = ? AND date >= ?
        """,
        (product, since),
    ).fetchone()
    conn.close()
    return row[0] if row and row[0] is not None else None
