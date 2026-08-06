from playwright.sync_api import sync_playwright

from scrapers.browser import USER_AGENT, launch_browser


def with_page(headless: bool = True):
    """Playwright + Chromium + uma página pronta."""
    playwright = sync_playwright().start()
    browser = launch_browser(playwright, headless=headless)
    page = browser.new_page(user_agent=USER_AGENT)
    return playwright, browser, page


def close_session(playwright, browser) -> None:
    browser.close()
    playwright.stop()
