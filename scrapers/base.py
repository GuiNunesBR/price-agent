import re
from abc import ABC, abstractmethod


def parse_brl(text: str) -> float | None:
    """Converte texto de preço brasileiro (R$ 1.234,56) para float."""
    if not text:
        return None
    cleaned = re.sub(r"[^\d,.]", "", text.strip())
    if not cleaned:
        return None
    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        parts = cleaned.split(".")
        if len(parts) > 2:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> float | None:
        pass
