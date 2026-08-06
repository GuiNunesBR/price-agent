from playwright.sync_api import Browser, Playwright

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def launch_browser(playwright: Playwright, *, headless: bool = True) -> Browser:
    return playwright.chromium.launch(headless=headless)
