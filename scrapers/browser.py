import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Browser, Playwright, sync_playwright

load_dotenv()

DEFAULT_BRAVE = Path(
    os.environ.get("ProgramFiles", r"C:\Program Files")
) / "BraveSoftware/Brave-Browser/Application/brave.exe"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def brave_executable() -> Path:
    custom = os.getenv("BRAVE_EXECUTABLE_PATH")
    if custom:
        return Path(custom)
    return DEFAULT_BRAVE


def launch_brave(playwright: Playwright, *, headless: bool = True) -> Browser:
    exe = brave_executable()
    if not exe.is_file():
        raise FileNotFoundError(
            f"Brave não encontrado em {exe}. "
            "Instale o Brave ou defina BRAVE_EXECUTABLE_PATH no .env"
        )
    return playwright.chromium.launch(
        executable_path=str(exe),
        headless=headless,
    )
