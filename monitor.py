import argparse
import json
import logging
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from database import create_db, get_last_price, save_price
from notifier import send_drop_alert, send_scrape_error, send_target_alert
from scrapers import get_price

load_dotenv()

PRODUCTS_FILE = Path(__file__).parent / "products.json"
DROP_THRESHOLD_PCT = 5.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("price-agent")


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def check_product(item: dict) -> None:
    name = item["name"]
    url = item["url"]
    target = float(item["target_price"])

    log.info("Buscando preço: %s", name)
    price = get_price(url)

    if price is None:
        log.warning("Preço não encontrado: %s", name)
        send_scrape_error(name, url)
        return

    log.info("%s → R$ %.2f", name, price)
    previous = get_last_price(name)
    save_price(name, price)

    if price <= target:
        send_target_alert(name, price, target, url)

    if previous and previous > price:
        pct = ((previous - price) / previous) * 100
        if pct >= DROP_THRESHOLD_PCT:
            send_drop_alert(name, price, previous, pct, url)


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
    import os

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
