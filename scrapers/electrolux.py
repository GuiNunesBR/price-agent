from urllib.parse import urlparse

import requests

from scrapers.base import BaseScraper

HEADERS = {"User-Agent": "Mozilla/5.0"}


def price_from_vtex(data: list) -> float | None:
    """Extrai o preco do primeiro produto de uma resposta da API de catalogo VTEX."""
    if not data:
        return None
    offer = data[0]["items"][0]["sellers"][0]["commertialOffer"]
    if not offer.get("IsAvailable"):
        return None
    price = offer.get("Price")
    if price and price > 0:
        return float(price)
    return None


class ElectroluxScraper(BaseScraper):
    def scrape(self, url: str) -> float | None:
        parsed = urlparse(url)
        api_url = f"{parsed.scheme}://{parsed.netloc}/api/catalog_system/pub/products/search{parsed.path}"
        response = requests.get(api_url, headers=HEADERS, timeout=30)
        if not response.ok:
            return None
        return price_from_vtex(response.json())
