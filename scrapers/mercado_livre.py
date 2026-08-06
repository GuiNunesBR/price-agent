from scrapers.base import BaseScraper, parse_brl
from scrapers.page import close_session, with_page


class MercadoLivreScraper(BaseScraper):
    SELECTORS = [
        ".andes-money-amount__fraction",
        "meta[itemprop='price']",
        ".ui-pdp-price__second-line .andes-money-amount",
    ]

    def scrape(self, url: str) -> float | None:
        playwright, browser, page = with_page(headless=False)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            meta = page.query_selector("meta[itemprop='price']")
            if meta:
                content = meta.get_attribute("content")
                if content:
                    try:
                        return float(content)
                    except ValueError:
                        pass
            for selector in self.SELECTORS:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text()
                    price = parse_brl(text)
                    if price and price > 0:
                        return price
        finally:
            close_session(playwright, browser)
        return None
