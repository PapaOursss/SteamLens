from dataclasses import dataclass
from datetime import datetime
from typing import Any

from django.db import transaction
from django.db.models import F

from ingestion.sources.twitch.steam_match import appids_by_igdb, appids_by_name
from ingestion.sources.twitch.stream_tally import StreamTally
from players.models import (
    TwitchCategory,
    TwitchLanguageDay,
    TwitchStreamSnapshot,
    TwitchTopSnapshot,
)

BOX_ART_SIZE = {"{width}": "144", "{height}": "192"}


@dataclass(frozen=True)
class RankedCategory:
    rank: int
    twitch_game: dict[str, Any]
    tally: StreamTally


def save_categories(twitch_games: list[dict[str, Any]]) -> dict[str, TwitchCategory]:
    """Crée ou met à jour les catégories, et relie au jeu Steam celles qui ne le sont pas encore."""
    categories = {}
    for twitch_game in twitch_games:
        category, _ = TwitchCategory.objects.update_or_create(
            twitch_id=str(twitch_game["id"]),
            defaults={
                "name": twitch_game.get("name") or "",
                "box_art_url": _box_art(twitch_game.get("box_art_url") or ""),
                "igdb_id": _igdb_id(twitch_game),
            },
        )
        categories[category.twitch_id] = category
    _link_to_steam([category for category in categories.values() if category.game_id is None])
    return categories


def save_snapshot(taken_at: datetime, ranked: list[RankedCategory]) -> int:
    """Un relevé par heure : relancer dans la même heure ne compte pas deux fois les langues."""
    categories = save_categories([entry.twitch_game for entry in ranked])
    rows = 0
    with transaction.atomic():
        for entry in ranked:
            category = categories[str(entry.twitch_game["id"])]
            _, created = TwitchTopSnapshot.objects.update_or_create(
                category=category,
                taken_at=taken_at,
                defaults={
                    "rank": entry.rank,
                    "viewer_count": entry.tally.viewers,
                    "stream_count": entry.tally.streams,
                },
            )
            rows += 1
            if created:
                rows += _add_language_hours(category, taken_at, entry.tally)
            if category.game_id is not None:
                TwitchStreamSnapshot.objects.update_or_create(
                    game_id=category.game_id,
                    taken_at=taken_at,
                    defaults={
                        "viewer_count": entry.tally.viewers,
                        "stream_count": entry.tally.streams,
                    },
                )
                rows += 1
    return rows


def _add_language_hours(category: TwitchCategory, taken_at: datetime, tally: StreamTally) -> int:
    day = taken_at.date()
    for language, viewers in tally.viewers_by_language.items():
        row, created = TwitchLanguageDay.objects.get_or_create(
            category=category, day=day, language=language, defaults={"viewer_hours": viewers}
        )
        if not created:
            TwitchLanguageDay.objects.filter(pk=row.pk).update(
                viewer_hours=F("viewer_hours") + viewers
            )
    return len(tally.viewers_by_language)


def _link_to_steam(categories: list[TwitchCategory]) -> None:
    if not categories:
        return
    by_igdb = appids_by_igdb(c.igdb_id for c in categories if c.igdb_id is not None)
    unmatched = [c for c in categories if by_igdb.get(c.igdb_id) is None]
    by_name = appids_by_name(c.name for c in unmatched)
    for category in categories:
        appid = by_igdb.get(category.igdb_id) or by_name.get(category.name)
        if appid is not None:
            category.game_id = appid
            category.save(update_fields=["game"])


def _box_art(url: str) -> str:
    for placeholder, size in BOX_ART_SIZE.items():
        url = url.replace(placeholder, size)
    return url


def _igdb_id(twitch_game: dict[str, Any]) -> int | None:
    value = str(twitch_game.get("igdb_id") or "")
    return int(value) if value.isdigit() else None
