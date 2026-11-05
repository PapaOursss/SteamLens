"""Indicateurs des cartes du monde : chacun renvoie `{iso3: valeur}`, prêt pour ECharts.

Ajouter une carte = écrire une fonction ici et l'inscrire dans `MAP_INDICATORS`.
"""

from collections.abc import Callable

from django.db.models import Avg, Count, Max, Sum

from catalog.models import Company
from geography.models import ProfileCountryCount
from pricing.models import PricePoint

PRICE_DECIMALS = 2

type MapValues = dict[str, float]


def studios_per_country() -> MapValues:
    """Nombre de studios et d'éditeurs par pays d'origine."""
    rows = (
        Company.objects.filter(country__isnull=False)
        .values("country__iso3")
        .annotate(value=Count("id"))
    )
    return {row["country__iso3"]: row["value"] for row in rows}


def average_price_eur() -> MapValues:
    """Prix moyen d'un jeu dans chaque pays, converti en euros."""
    rows = (
        PricePoint.objects.filter(price_eur__isnull=False)
        .values("country__iso3")
        .annotate(value=Avg("price_eur"))
    )
    return {row["country__iso3"]: round(float(row["value"]), PRICE_DECIMALS) for row in rows}


def declared_profile_countries() -> MapValues:
    """Profils publics par pays déclaré, parmi les auteurs d'avis récents (T-37)."""
    latest = ProfileCountryCount.objects.aggregate(day=Max("date"))["day"]
    rows = (
        ProfileCountryCount.objects.filter(date=latest)
        .values("country__iso3")
        .annotate(value=Sum("profiles"))
    )
    return {row["country__iso3"]: row["value"] for row in rows}


MAP_INDICATORS: dict[str, Callable[[], MapValues]] = {
    "studios": studios_per_country,
    "average-price-eur": average_price_eur,
    "profile-countries": declared_profile_countries,
}
