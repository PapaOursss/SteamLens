from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from geography.country_table import ensure_countries
from pricing.euro_converter import EuroConverter
from pricing.models import PricePoint

USA = "US"
HUNDRED = Decimal(100)


@dataclass(frozen=True)
class UsdPrice:
    """Prix en dollars du Store américain relevé dans un dataset Kaggle."""

    appid: int
    final: Decimal
    initial: Decimal | None = None

    @property
    def discount_percent(self) -> int:
        if not self.initial or self.final >= self.initial:
            return 0
        ratio = (1 - self.final / self.initial) * HUNDRED
        return int(ratio.quantize(Decimal(1), rounding=ROUND_HALF_UP))


def save_usd_prices(
    prices: list[UsdPrice], source: str, day: date, converter: EuroConverter
) -> int:
    """Range les prix dans `PricePoint` (États-Unis, date des données), sans doublon."""
    ensure_countries({USA})
    PricePoint.objects.bulk_create(
        [
            PricePoint(
                game_id=price.appid,
                country_id=USA,
                currency="USD",
                price=price.final,
                price_eur=converter.to_eur(price.final, "USD"),
                discount_percent=price.discount_percent,
                date=day,
                source=source,
            )
            for price in prices
        ],
        update_conflicts=True,
        unique_fields=["game", "country", "date", "source"],
        update_fields=["price", "price_eur", "discount_percent"],
    )
    return len(prices)
