"""Ce que raconte l'historique des prix d'un jeu : plus bas, promos par an, remise moyenne."""

from collections import Counter
from collections.abc import Sequence
from itertools import pairwise

from pricing.models import PriceChange

CUT_DECIMALS = 1


def promo_starts(changes: Sequence[PriceChange]) -> list[PriceChange]:
    """Les changements qui ouvrent une promo : une remise après un prix plein (ou au début)."""
    ordered = sorted(changes, key=lambda change: change.changed_at)
    if not ordered:
        return []
    starts = [ordered[0]] if ordered[0].cut else []
    starts += [after for before, after in pairwise(ordered) if after.cut and not before.cut]
    return starts


def history_summary(changes: Sequence[PriceChange]) -> dict:
    starts = promo_starts(changes)
    lowest = min(changes, key=lambda change: change.price, default=None)
    per_year = Counter(start.changed_at.year for start in starts)
    years = {change.changed_at.year for change in changes}
    return {
        "lowest_price": float(lowest.price) if lowest else None,
        "lowest_date": lowest.changed_at.date() if lowest else None,
        "promotions": len(starts),
        "promotions_per_year": round(len(starts) / len(years), CUT_DECIMALS) if years else 0.0,
        "average_cut": round(sum(start.cut for start in starts) / len(starts), CUT_DECIMALS)
        if starts
        else 0.0,
        "by_year": [{"year": year, "promotions": per_year[year]} for year in sorted(years)],
    }
