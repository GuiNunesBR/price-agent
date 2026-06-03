from playwright.sync_api import sync_playwright

from scrapers.browser import USER_AGENT, launch_brave


def with_brave_page(headless: bool = True):
    """Context manager: Playwright + Brave + uma página pronta."""
    playwright = sync_playwright().start()
    browser = launch_brave(playwright, headless=headless)
    page = browser.new_page(user_agent=USER_AGENT)
    return playwright, browser, page


def close_session(playwright, browser) -> None:
    browser.close()
    playwright.stop()
