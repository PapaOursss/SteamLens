from dataclasses import dataclass
from decimal import Decimal
from typing import Any

MINOR_UNITS_PER_UNIT = 100


@dataclass(frozen=True)
class StorePrice:
    """Prix d'un jeu dans un pays, dans la devise locale.

    Steam donne toujours ses montants en centièmes, même pour le yen ou le won.
    """

    appid: int
    country_code: str
    currency: str
    initial_amount: Decimal
    final_amount: Decimal
    discount_percent: int

    @classmethod
    def from_price_overview(
        cls, appid: int, country_code: str, price_overview: dict[str, Any]
    ) -> "StorePrice":
        return cls(
            appid=appid,
            country_code=country_code.upper(),
            currency=price_overview["currency"],
            initial_amount=_to_units(price_overview["initial"]),
            final_amount=_to_units(price_overview["final"]),
            discount_percent=int(price_overview.get("discount_percent") or 0),
        )


def _to_units(minor_units: int) -> Decimal:
    return Decimal(int(minor_units)) / MINOR_UNITS_PER_UNIT
