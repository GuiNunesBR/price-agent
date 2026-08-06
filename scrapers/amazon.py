from scrapers.base import BaseScraper, parse_brl
from scrapers.page import close_session, with_page


class AmazonScraper(BaseScraper):
    SELECTORS = [
        ".a-price .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-offscreen",
        "#priceblock_ourprice",
        ".a-price-whole",
    ]

    def scrape(self, url: str) -> float | None:
        playwright, browser, page = with_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(2000)
            for selector in self.SELECTORS:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text() or el.get_attribute("textContent") or ""
                    price = parse_brl(text)
                    if price and price > 0:
                        return price
        finally:
            close_session(playwright, browser)
        return None
