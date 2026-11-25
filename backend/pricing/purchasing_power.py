"""Combien d'heures de travail coûte un jeu selon le pays (T-25).

Heure de travail = PIB par habitant en parité de pouvoir d'achat ÷ heures d'une année pleine.
C'est un ordre de grandeur : le PIB n'est pas un salaire, et le prix est en euros courants.
"""

from catalog.models import Game
from geography.models import CountryIndicator

HOURS_PER_YEAR = 2080
REFERENCE_COUNTRY = "US"
EXAMPLE_PRICE_EUR = 60.0
DECIMALS = 2


def latest_prices(game: Game) -> dict[str, float]:
    """Dernier prix en euros de chaque pays."""
    points = game.prices.filter(price_eur__isnull=False).order_by("date")
    return {point.country_id: float(point.price_eur) for point in points}


def _hours(price: float | None, income: float) -> float | None:
    return None if price is None else round(price * HOURS_PER_YEAR / income, DECIMALS)


def purchasing_power(game: Game | None) -> dict:
    """Sans prix relevé, le jeu d'exemple à 60 € partout."""
    prices = latest_prices(game) if game else {}
    uniform = prices.get(REFERENCE_COUNTRY) if prices else EXAMPLE_PRICE_EUR
    incomes = CountryIndicator.objects.filter(
        indicator=CountryIndicator.GDP_PER_CAPITA, value__gt=0
    ).select_related("country")
    rows = [
        {
            "iso3": income.country.iso3,
            "name": income.country.name_fr,
            "income": round(income.value),
            "year": income.year,
            "price_eur": prices.get(income.country_id),
            "hours": _hours(prices.get(income.country_id), income.value),
            "hours_uniform": _hours(uniform, income.value),
        }
        for income in incomes
    ]
    rows.sort(key=lambda row: row["hours"] or row["hours_uniform"] or 0, reverse=True)
    return {
        "appid": game.appid if game else None,
        "name": game.name if game else None,
        "uniform_price_eur": uniform,
        "has_local_prices": bool(prices),
        "countries": rows,
    }
