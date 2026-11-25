from collections.abc import Iterable

from django.db import transaction

from catalog.models import Company, Game
from geography.country_table import BY_ISO2, ensure_countries
from geography.models import Country
from ingestion.sources.wikidata.wikidata_client import GameStudio, StudioCountry


@transaction.atomic
def save_studios(studios: Iterable[GameStudio]) -> int:
    """Relie chaque jeu à ses studios et donne un pays aux studios qui n'en ont pas.

    Un pays déjà posé (par IGDB, T-11) n'est jamais remplacé : les deux sources se complètent.
    """
    known_games = set(Game.objects.values_list("appid", flat=True))
    links = Game.developers.through
    rows = 0
    companies: dict[str, Company] = {}
    for studio in studios:
        if studio.appid not in known_games:
            continue
        company = companies.get(studio.name.casefold()) or _company(studio.name)
        companies[studio.name.casefold()] = company
        if company.country_id is None and studio.country is not None:
            company.country_id = _ensure_country(studio.country)
            company.save(update_fields=["country"])
        _, created = links.objects.get_or_create(game_id=studio.appid, company_id=company.id)
        rows += int(created)
    return rows


def _company(name: str) -> Company:
    existing = Company.objects.filter(name__iexact=name).order_by("id").first()
    return existing or Company.objects.create(name=name)


def _ensure_country(country: StudioCountry) -> str:
    """Les pays de la table d'abord (noms et continents relus) ; sinon celui de Wikidata."""
    if country.iso2 in BY_ISO2:
        ensure_countries({country.iso2})
    else:
        Country.objects.get_or_create(
            iso2=country.iso2,
            defaults={"iso3": country.iso3, "name_fr": country.name or country.iso3},
        )
    return country.iso2
