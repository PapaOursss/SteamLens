from typing import Any

from django.db import transaction

from catalog.models import Game, GamePlaytime, Tag
from ingestion.writing import ensure_named


@transaction.atomic
def save_rawg_game_data(appid: int, rawg_data: dict[str, Any]) -> bool:
    """Enregistre les informations RAWG pour un jeu : notes, metacritic, screenshots, playtime, tags."""
    game = Game.objects.filter(appid=appid).first()
    if not game:
        return False

    rawg_id = rawg_data.get("id")
    if rawg_id and (game.rawg_id is None or game.rawg_id == rawg_id):
        game.rawg_id = rawg_id

    rating = rawg_data.get("rating")
    if rating is not None:
        game.rawg_rating = float(rating)

    metacritic = rawg_data.get("metacritic")
    if metacritic and game.metacritic_score is None:
        game.metacritic_score = int(metacritic)

    screenshots = rawg_data.get("screenshots") or rawg_data.get("short_screenshots") or []
    if screenshots:
        existing = set(game.screenshots or [])
        new_shots = [s if isinstance(s, str) else s.get("image") for s in screenshots]
        for shot in new_shots:
            if shot and shot not in existing:
                existing.add(shot)
        game.screenshots = list(existing)

    game.save()

    _save_playtime(game, rawg_data)
    _save_tags(game, rawg_data)
    return True


def _save_playtime(game: Game, rawg_data: dict[str, Any]) -> None:
    playtime_hours = rawg_data.get("playtime")
    if playtime_hours and playtime_hours > 0:
        minutes = int(playtime_hours * 60)
        playtime, created = GamePlaytime.objects.get_or_create(game=game)
        if created or playtime.average_playtime_minutes == 0:
            playtime.average_playtime_minutes = minutes
        if created or playtime.median_playtime_minutes == 0:
            playtime.median_playtime_minutes = minutes
        playtime.save()


def _save_tags(game: Game, rawg_data: dict[str, Any]) -> None:
    rawg_tags = rawg_data.get("tags") or []
    tag_names = {t.get("name") for t in rawg_tags if t.get("name") and t.get("language") in ("eng", None)}
    if not tag_names:
        return
    ids = ensure_named(Tag, tag_names)
    through = Game.tags.through
    through.objects.bulk_create(
        [through(game_id=game.appid, tag_id=ids[name], votes=1) for name in tag_names if name in ids],
        ignore_conflicts=True,
    )
