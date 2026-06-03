"""Consultas rapidas ao historico de precos."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from database import create_db, get_price_stats


def money(value: float | None) -> str:
    if value is None:
        return "-"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("product", help="Nome do produto (como em products.json)")
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    create_db()
    stats = get_price_stats(args.product, args.days)
    if stats["samples"] == 0:
        print(f"Sem historico para '{args.product}' nos ultimos {args.days} dias.")
        return

    print(f"Historico de '{args.product}' nos ultimos {args.days} dias")
    print(f"Amostras: {stats['samples']}")
    print(f"Menor preco: {money(stats['minimum'])}")
    print(f"Preco medio: {money(stats['average'])}")
    print(f"Maior preco: {money(stats['maximum'])}")


if __name__ == "__main__":
    main()
