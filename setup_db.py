import json
from pathlib import Path

from database import DB, create_db, upsert_product

PRODUCTS_FILE = Path(__file__).parent / "products.json"


def main() -> None:
    create_db()
    products = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    for product in products:
        product_id = upsert_product(product)
        print(f"Produto cadastrado no SQLite: #{product_id} {product['name']}")
    print(f"Banco pronto em: {DB}")


if __name__ == "__main__":
    main()
