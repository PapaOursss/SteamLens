from decimal import ROUND_HALF_UP, Decimal

from ingestion.sources.json_fetcher import JsonFetcher, cached_fetcher

FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"
CENT = Decimal("0.01")


class EuroConverter:
    """Convertit un prix en euros avec les taux du jour de la BCE (Frankfurter, sans clé).

    Une devise que la BCE ne publie pas (peso argentin, tenge…) donne None.
    """

    def __init__(self, rates: dict[str, Decimal]) -> None:
        self.rates = {"EUR": Decimal(1), **rates}

    @classmethod
    def from_frankfurter(cls, fetch_json: JsonFetcher | None = None) -> "EuroConverter":
        fetch = fetch_json or cached_fetcher("frankfurter")
        body = fetch(FRANKFURTER_URL, {"base": "EUR"})
        return cls({currency: Decimal(str(rate)) for currency, rate in body["rates"].items()})

    def to_eur(self, amount: Decimal, currency: str) -> Decimal | None:
        rate = self.rates.get(currency.upper())
        if not rate:
            return None
        return (amount / rate).quantize(CENT, rounding=ROUND_HALF_UP)
