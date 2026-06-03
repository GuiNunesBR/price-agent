import sqlite3

from database import DB, create_db


def print_rows(title: str, rows: list[sqlite3.Row]) -> None:
    print(f"\n{title}:")
    if not rows:
        print("- nenhum registro")
        return
    for row in rows:
        print(dict(row))


def main() -> None:
    create_db()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    print("Tabelas:")
    for table in tables:
        print(f"- {table['name']}")

    products = conn.execute(
        """
        SELECT id, name, brand, model, target_min, target_max, priority, status
        FROM products
        ORDER BY id
        """
    ).fetchall()
    print_rows("Produtos", products)

    offers = conn.execute(
        """
        SELECT id, product_id, title, price, store, source, score, captured_at
        FROM offers
        ORDER BY captured_at DESC
        LIMIT 10
        """
    ).fetchall()
    print_rows("Ultimas ofertas", offers)

    alerts = conn.execute(
        """
        SELECT id, product_id, offer_id, reason, message, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 10
        """
    ).fetchall()
    print_rows("Ultimos alertas", alerts)
    conn.close()


if __name__ == "__main__":
    main()
