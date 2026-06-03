from scrapers.base import BaseScraper, parse_brl
from scrapers.page import close_session, with_brave_page


class KabumScraper(BaseScraper):
    SELECTORS = [
        "h4.text-2xl.font-bold.text-orange-500",
        ".finalPrice",
        "[class*='priceCard']",
        "span[class*='Price']",
    ]

    def scrape(self, url: str) -> float | None:
        playwright, browser, page = with_brave_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
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
