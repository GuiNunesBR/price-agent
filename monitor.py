import argparse
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from database import (
    count_consecutive_failures,
    create_db,
    get_last_price,
    record_scrape_failure,
    save_price,
    upsert_product,
)
from notifier import (
    send_drop_alert,
    send_scrape_error,
    send_scrape_recovered,
    send_target_alert,
)
from scrapers import get_scraper

load_dotenv()

PRODUCTS_FILE = Path(__file__).parent / "products.json"
DROP_THRESHOLD_PCT = 15.0
# Falhas seguidas de scrape antes de avisar no Telegram (uma vez por sequencia).
FAILURE_ALERT_AFTER = max(1, int(os.getenv("SCRAPE_FAILURE_ALERT_AFTER", "3")))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("price-agent")


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def decide_alerts(
    price: float, target: float, previous: float | None
) -> tuple[bool, float | None]:
    """Decide quais alertas disparar para um preco coletado.

    Retorna (meta_atingida, queda_pct). queda_pct e None quando nao ha preco
    anterior ou a queda nao chega a DROP_THRESHOLD_PCT.
    """
    hit_target = price <= target
    pct_drop = None
    if previous and previous > price:
        pct = ((previous - price) / previous) * 100
        if pct >= DROP_THRESHOLD_PCT:
            pct_drop = pct
    return hit_target, pct_drop


def should_alert_failure(consecutive: int, threshold: int) -> bool:
    """Avisa uma unica vez por sequencia de falhas: quando ela atinge o limite."""
    return consecutive == threshold


def scrape_recovered(failures_before: int, threshold: int) -> bool:
    """O scraper voltou depois de uma sequencia que ja tinha gerado alerta."""
    return failures_before >= threshold


def store_from_url(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def handle_scrape_failure(name: str, url: str, reason: str) -> None:
    log.warning("Preço não encontrado: %s (%s)", name, reason)
    record_scrape_failure(name, url, store_from_url(url), reason)
    consecutive = count_consecutive_failures(name)
    if should_alert_failure(consecutive, FAILURE_ALERT_AFTER):
        send_scrape_error(name, url, consecutive, reason)


def check_product(item: dict) -> None:
    name = item["name"]
    upsert_product(item)

    url = item.get("url")
    price_range = item.get("target_price_range") or {}
    target = float(item.get("target_price", price_range.get("max", 0)))

    if not url:
        log.info(
            "%s cadastrado no banco. Busca por fontes ainda sera implementada.",
            name,
        )
        return

    log.info("Buscando preço: %s", name)
    # Loja sem scraper e erro de configuracao: o ValueError sobe para run().
    scraper = get_scraper(url)
    try:
        price = scraper.scrape(url)
        reason = "preco_nao_encontrado"
    except Exception as e:  # rede, timeout, anti-bot, layout novo da pagina
        log.exception("Scraper falhou: %s", name)
        price = None
        reason = f"{type(e).__name__}: {e}"[:300]

    if price is None:
        handle_scrape_failure(name, url, reason)
        return

    failures_before = count_consecutive_failures(name)
    log.info("%s → R$ %.2f", name, price)
    previous = get_last_price(name)
    save_price(name, price)
    if scrape_recovered(failures_before, FAILURE_ALERT_AFTER):
        send_scrape_recovered(name, url, failures_before)

    hit_target, pct_drop = decide_alerts(price, target, previous)
    if hit_target:
        send_target_alert(name, price, target, url)
    if pct_drop is not None:
        send_drop_alert(name, price, previous, pct_drop, url)


def run() -> None:
    create_db()
    products = load_products()
    for item in products:
        try:
            check_product(item)
        except ValueError as e:
            log.error("%s: %s", item.get("name", "?"), e)
        except Exception:
            log.exception("Erro em %s", item.get("name", "?"))


def run_scheduled() -> None:
    hour = int(os.getenv("SCHEDULE_HOUR", "9"))
    minute = int(os.getenv("SCHEDULE_MINUTE", "0"))

    scheduler = BlockingScheduler()
    scheduler.add_job(run, "cron", hour=hour, minute=minute, id="daily_monitor")
    log.info("Agendado: todo dia às %02d:%02d", hour, minute)
    run()
    scheduler.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agente monitor de preços")
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Executa uma vez e depois agenda busca diária (APScheduler)",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        run()


if __name__ == "__main__":
    main()
