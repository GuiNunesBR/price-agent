from urllib.parse import urlparse

from scrapers.amazon import AmazonScraper
from scrapers.base import BaseScraper
from scrapers.kabum import KabumScraper
from scrapers.mercado_livre import MercadoLivreScraper


def get_scraper(url: str) -> BaseScraper:
    host = urlparse(url).netloc.lower()
    if "amazon" in host:
        return AmazonScraper()
    if "mercadolivre" in host or "mercadolibre" in host:
        return MercadoLivreScraper()
    if "kabum" in host:
        return KabumScraper()
    raise ValueError(f"Nenhum scraper registrado para: {host}")


def get_price(url: str) -> float | None:
    scraper = get_scraper(url)
    return scraper.scrape(url)
