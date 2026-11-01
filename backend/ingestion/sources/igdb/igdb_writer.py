from collections.abc import Iterable
from typing import Any

from django.db import models, transaction

from catalog.models import Company, Game, GameMode, Genre, IgdbPopularity, PlayerPerspective, Theme
from geography.country_table import BY_NUMERIC, ensure_countries
from ingestion.writing import ensure_named

LINKS: tuple[tuple[str, type[models.Model], Any, str], ...] = (
    ("genres", Genre, Game.igdb_genres.through, "genre_id"),
    ("themes", Theme, Game.themes.through, "theme_id"),
    ("game_modes", GameMode, Game.game_modes.through, "gamemode_id"),
    (
        "player_perspectives",
        PlayerPerspective,
        Game.player_perspectives.through,
        "playerperspective_id",
    ),
)


@transaction.atomic
def save_igdb_games(links: dict[int, int], games: list[dict[str, Any]]) -> int:
    """Relie chaque appid à son jeu IGDB et ajoute sa classification, ses studios et leurs pays.

    `links` : appid → id IGDB. Un id IGDB déjà pris par un autre appid (éditions d'un même
    jeu) n'est rangé que sur le premier.
    """
    appids_by_igdb: dict[int, list[int]] = {}
    for appid, igdb_id in links.items():
        appids_by_igdb.setdefault(igdb_id, []).append(appid)
    _store_igdb_ids(appids_by_igdb)
    for key, entity, through, column in LINKS:
        pairs = {
            (appid, item["name"])
            for game in games
            for appid in appids_by_igdb.get(game["id"], [])
            for item in game.get(key, [])
            if item.get("name")
        }
        ids = ensure_named(entity, {name for _, name in pairs})
        through.objects.bulk_create(
            [through(game_id=appid, **{column: ids[name]}) for appid, name in pairs if name in ids],
            ignore_conflicts=True,
        )
    _save_companies(appids_by_igdb, games)
    return len(games)


def _store_igdb_ids(appids_by_igdb: dict[int, list[int]]) -> None:
    taken = dict(Game.objects.filter(igdb_id__in=appids_by_igdb).values_list("igdb_id", "appid"))
    for igdb_id, appids in appids_by_igdb.items():
        owner = taken.get(igdb_id, min(appids))
        if owner in appids:
            Game.objects.filter(appid=owner).update(igdb_id=igdb_id)


def _save_companies(appids_by_igdb: dict[int, list[int]], games: list[dict[str, Any]]) -> None:
    involvements = [
        (appid, involved)
        for game in games
        for appid in appids_by_igdb.get(game["id"], [])
        for involved in game.get("involved_companies", [])
        if (involved.get("company") or {}).get("name")
    ]
    ids = ensure_named(Company, {involved["company"]["name"] for _, involved in involvements})
    for role, through in (
        ("developer", Game.developers.through),
        ("publisher", Game.publishers.through),
    ):
        through.objects.bulk_create(
            [
                through(game_id=appid, company_id=ids[involved["company"]["name"]])
                for appid, involved in involvements
                if involved.get(role) and involved["company"]["name"] in ids
            ],
            ignore_conflicts=True,
        )
    _set_company_countries(involvements, ids)


def _set_company_countries(involvements: Iterable[tuple[int, dict]], ids: dict[str, int]) -> None:
    """Pays du studio (code ISO numérique chez IGDB), sans écraser un pays déjà connu."""
    iso2_by_company: dict[int, str] = {}
    for _, involved in involvements:
        row = BY_NUMERIC.get(involved["company"].get("country") or 0)
        if row is not None and involved["company"]["name"] in ids:
            iso2_by_company[ids[involved["company"]["name"]]] = row.iso2
    known = ensure_countries(set(iso2_by_company.values()))
    for company_id, iso2 in iso2_by_company.items():
        if iso2 in known:
            Company.objects.filter(id=company_id, country__isnull=True).update(country_id=iso2)


def save_popularity(
    links: dict[int, int], types: dict[int, str], primitives: list[dict[str, Any]]
) -> int:
    appids_by_igdb: dict[int, list[int]] = {}
    for appid, igdb_id in links.items():
        appids_by_igdb.setdefault(igdb_id, []).append(appid)
    scores = {
        (appid, types.get(row["popularity_type"], f"type {row['popularity_type']}")): float(
            row["value"]
        )
        for row in primitives
        for appid in appids_by_igdb.get(row.get("game_id"), [])
    }
    IgdbPopularity.objects.bulk_create(
        [
            IgdbPopularity(game_id=appid, popularity_type=kind, value=value)
            for (appid, kind), value in scores.items()
        ],
        update_conflicts=True,
        unique_fields=["game", "popularity_type"],
        update_fields=["value", "updated_at"],
    )
    return len(scores)
