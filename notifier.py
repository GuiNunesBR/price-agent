import html
import os

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _format_brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def send_message(text: str) -> bool:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        response = requests.post(
            TELEGRAM_API.format(token=token),
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=30,
        )
        if not response.ok:
            print(f"[notifier] Telegram recusou ({response.status_code}): {response.text[:200]}")
        return response.ok
    print(text)
    return True


def send_target_alert(product: str, current: float, target: float, url: str) -> None:
    text = (
        f"🔥 <b>ALERTA DE PREÇO — meta atingida</b>\n\n"
        f"<b>Produto:</b> {product}\n"
        f"<b>Atual:</b> {_format_brl(current)}\n"
        f"<b>Meta:</b> {_format_brl(target)}\n"
        f"<b>Link:</b> {url}"
    )
    send_message(text)


def send_drop_alert(
    product: str,
    current: float,
    previous: float,
    pct_drop: float,
    url: str,
) -> None:
    text = (
        f"📉 <b>QUEDA DE PREÇO</b>\n\n"
        f"<b>Produto:</b> {product}\n"
        f"<b>Atual:</b> {_format_brl(current)}\n"
        f"<b>Anterior:</b> {_format_brl(previous)}\n"
        f"<b>Queda:</b> {pct_drop:.1f}%\n"
        f"<b>Link:</b> {url}"
    )
    send_message(text)


def send_scrape_error(product: str, url: str, consecutive: int, reason: str) -> None:
    text = (
        f"⚠️ <b>Falha ao buscar preço</b>\n\n"
        f"<b>Produto:</b> {product}\n"
        f"<b>Link:</b> {url}\n"
        f"<b>Falhas seguidas:</b> {consecutive}\n"
        f"<b>Último erro:</b> {html.escape(reason)}\n"
        f"Verifique URL e seletores do scraper."
    )
    send_message(text)


def send_scrape_recovered(product: str, url: str, failures: int) -> None:
    text = (
        f"✅ <b>Scraper voltou a funcionar</b>\n\n"
        f"<b>Produto:</b> {product}\n"
        f"<b>Link:</b> {url}\n"
        f"Preço capturado de novo depois de {failures} falhas seguidas."
    )
    send_message(text)
