"""Mostra o conteudo do banco: produtos, ofertas, alertas e falhas de scrape.

Uso:
    python inspect_db.py
"""

from database import connect, create_db


def print_rows(title: str, rows: list[dict]) -> None:
    print(f"\n{title}:")
    if not rows:
        print("- nenhum registro")
        return
    for row in rows:
        print(dict(row))


def main() -> None:
    create_db()
    conn = connect()

    tables = conn.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """
    ).fetchall()
    print("Tabelas:")
    for table in tables:
        print(f"- {table['table_name']}")

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

    failures = conn.execute(
        """
        SELECT product, store, reason, failed_at
        FROM scrape_failures
        ORDER BY failed_at DESC
        LIMIT 10
        """
    ).fetchall()
    print_rows("Ultimas falhas de scrape", failures)
    conn.close()


if __name__ == "__main__":
    main()
