"""Busca candidatos nas lojas VTEX cadastradas e salva o resultado em JSON.

Uso:
    python busca.py "geladeira inverter"
    python busca.py "lava e seca" --limite 5

Primeira versao do Search Agent (ver PROJECT_SCOPE.md): busca so em lojas com
API VTEX aberta. Agregadores (Buscape/Zoom) ficam fora por anti-bot.
"""

import argparse
import json
from pathlib import Path

import requests

LOJAS_VTEX = {
    "electrolux": "https://loja.electrolux.com.br",
    "consul": "https://loja.consul.com.br",
}
HEADERS = {"User-Agent": "Mozilla/5.0"}
ARQUIVO_RESULTADO = Path(__file__).parent / "ultima_busca.json"


def buscar_na_loja(loja: str, base: str, termo: str, limite: int) -> list[dict]:
    url = f"{base}/api/catalog_system/pub/products/search/?ft={termo}&_from=0&_to={limite - 1}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    if not response.ok:
        return []

    candidatos = []
    for produto in response.json():
        try:
            offer = produto["items"][0]["sellers"][0]["commertialOffer"]
        except (KeyError, IndexError):
            continue
        preco = offer.get("Price")
        if not offer.get("IsAvailable") or not preco or preco <= 0:
            continue
        candidatos.append(
            {
                "loja": loja,
                "nome": produto.get("productName"),
                "preco": float(preco),
                "url": f"{base}/{produto.get('linkText')}/p",
            }
        )
    return candidatos


def buscar(termo: str, limite: int) -> list[dict]:
    resultados = []
    for loja, base in LOJAS_VTEX.items():
        try:
            resultados.extend(buscar_na_loja(loja, base, termo, limite))
        except requests.RequestException as e:
            print(f"[busca] {loja} falhou: {e}")
    return sorted(resultados, key=lambda c: c["preco"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Busca produto nas lojas VTEX cadastradas")
    parser.add_argument("termo", help="termo de busca, ex.: 'geladeira inverter'")
    parser.add_argument("--limite", type=int, default=10, help="max de resultados por loja")
    args = parser.parse_args()

    resultados = buscar(args.termo, args.limite)
    if not resultados:
        print("Nenhum candidato encontrado.")
        return

    for c in resultados:
        print(f"R$ {c['preco']:>9.2f} | {c['loja']:<10} | {c['nome']}")
    ARQUIVO_RESULTADO.write_text(
        json.dumps({"termo": args.termo, "candidatos": resultados}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{len(resultados)} candidatos salvos em {ARQUIVO_RESULTADO.name}")


if __name__ == "__main__":
    main()
