import re
import unicodedata
from dataclasses import dataclass


DROP_THRESHOLD_PCT = 15.0


@dataclass(frozen=True)
class OpportunityResult:
    matches_product: bool
    should_alert: bool
    score: float
    reasons: list[str]


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


def keyword_hits(title: str, keywords: list[str]) -> int:
    normalized_title = normalize_text(title)
    return sum(1 for keyword in keywords if normalize_text(keyword) in normalized_title)


def has_blocked_keyword(title: str, blocked_keywords: list[str]) -> bool:
    return keyword_hits(title, blocked_keywords) > 0


def matches_required_keywords(title: str, required_keywords: list[str]) -> bool:
    if not required_keywords:
        return True
    return keyword_hits(title, required_keywords) == len(required_keywords)


def evaluate_offer(
    product: dict,
    *,
    title: str,
    price: float,
    previous_min: float | None = None,
) -> OpportunityResult:
    required_keywords = product.get("required_keywords") or []
    blocked_keywords = product.get("blocked_keywords") or []
    price_range = product.get("target_price_range") or {}
    target_min = price_range.get("min")
    target_max = product.get("target_price", price_range.get("max"))

    reasons: list[str] = []
    score = 0.0

    if has_blocked_keyword(title, blocked_keywords):
        return OpportunityResult(
            matches_product=False,
            should_alert=False,
            score=0.0,
            reasons=["blocked_keyword"],
        )

    required_hits = keyword_hits(title, required_keywords)
    if required_keywords:
        score += (required_hits / len(required_keywords)) * 40

    matches_product = matches_required_keywords(title, required_keywords)
    if matches_product:
        reasons.append("required_keywords_matched")
    else:
        reasons.append("missing_required_keywords")

    in_range = False
    if target_max is not None:
        if target_min is None:
            in_range = price <= float(target_max)
        else:
            in_range = float(target_min) <= price <= float(target_max)
        if in_range:
            score += 40
            reasons.append("price_in_target_range")

    dropped_enough = False
    if previous_min and previous_min > price:
        pct_drop = ((previous_min - price) / previous_min) * 100
        if pct_drop >= DROP_THRESHOLD_PCT:
            dropped_enough = True
            score += 20
            reasons.append(f"price_drop_{pct_drop:.1f}%")

    should_alert = matches_product and (in_range or dropped_enough)
    return OpportunityResult(
        matches_product=matches_product,
        should_alert=should_alert,
        score=min(score, 100.0),
        reasons=reasons,
    )
