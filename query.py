"""Consultas rápidas ao histórico (base para RAG/agente depois)."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import create_db, get_min_price_days


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", help="Nome do produto (como em products.json)")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    create_db()
    minimum = get_min_price_days(args.product, args.days)
    if minimum is None:
        print(f"Sem histórico para '{args.product}' nos últimos {args.days} dias.")
        return
    print(
        f"Menor preço de '{args.product}' nos últimos {args.days} dias: "
        f"R$ {minimum:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )


if __name__ == "__main__":
    main()
