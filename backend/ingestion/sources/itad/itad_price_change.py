from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ItadPriceChange:
    """Un changement de prix sur Steam renvoyé par `games/history`."""

    changed_at: datetime
    currency: str
    price: Decimal
    regular: Decimal
    cut: int
