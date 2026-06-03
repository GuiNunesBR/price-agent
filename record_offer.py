import argparse

from database import (
    create_db,
    get_min_price_days,
    get_product,
    save_alert,
    save_offer,
)
from opportunity import evaluate_offer


def main() -> None:
    parser = argparse.ArgumentParser(description="Registra uma oferta manualmente.")
    parser.add_argument("product", help="Nome do produto cadastrado no SQLite")
    parser.add_argument("--title", required=True, help="Titulo da oferta encontrada")
    parser.add_argument("--price", required=True, type=float, help="Preco da oferta")
    parser.add_argument("--source", required=True, help="Fonte: zoom, amazon, etc.")
    parser.add_argument("--store", default=None, help="Loja da oferta")
    parser.add_argument("--url", default=None, help="Link da oferta")
    args = parser.parse_args()

    create_db()
    product = get_product(args.product)
    if product is None:
        raise SystemExit(
            f"Produto nao encontrado: {args.product}. Rode python setup_db.py primeiro."
        )

    previous_min = get_min_price_days(args.product, days=365)
    result = evaluate_offer(
        product,
        title=args.title,
        price=args.price,
        previous_min=previous_min,
    )
    offer_id = save_offer(
        args.product,
        args.title,
        args.price,
        args.source,
        store=args.store,
        url=args.url,
        score=result.score,
    )

    print(f"Oferta registrada: #{offer_id}")
    print(f"Combina com produto: {result.matches_product}")
    print(f"Score: {result.score:.1f}")
    print(f"Motivos: {', '.join(result.reasons)}")

    if result.should_alert:
        message = (
            f"Oportunidade para {args.product}: {args.title} por R$ {args.price:.2f}"
        )
        alert_id = save_alert(
            args.product,
            reason=";".join(result.reasons),
            message=message,
            offer_id=offer_id,
        )
        print(f"Alerta registrado: #{alert_id}")
    else:
        print("Alerta nao registrado: oferta fora dos criterios.")


if __name__ == "__main__":
    main()
