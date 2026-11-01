from collections.abc import Iterable
from datetime import date
from itertools import batched
from typing import Any

from django.db import models, transaction

from catalog.models import Company, Game, GamePlaytime, GameTag, Genre, Platform, ReviewSummary, Tag
from ingestion.writing.game_record import GameRecord

BATCH_SIZE = 500
ALL_LANGUAGES = "all"
NAME_LENGTHS = {Genre: 100, Tag: 100, Platform: 100, Company: 255}


def is_empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


class GameWriter:
    """Écrit des `GameRecord` en base par paquets, sans jamais dupliquer.

    `data_date` est la date des données de la source : sur un jeu déjà rempli par une source
    plus récente, on ne fait que combler les champs vides. Les liens (genres, tags…)
    s'ajoutent toujours ; les votes de tags, le temps de jeu et les avis se mettent à jour.
    """

    def __init__(self, data_date: date, review_language: str = ALL_LANGUAGES) -> None:
        self.data_date = data_date
        self.review_language = review_language

    def save(self, records: Iterable[GameRecord]) -> int:
        saved = 0
        for batch in batched(records, BATCH_SIZE):
            with transaction.atomic():
                self._save_batch(_merge_duplicates(batch))
            saved += len(batch)
        return saved

    def _save_batch(self, records: list[GameRecord]) -> None:
        existing = Game.objects.in_bulk([record.appid for record in records])
        to_create: list[Game] = []
        to_update: list[Game] = []
        touched: set[str] = set()
        fresher: list[GameRecord] = []
        for record in records:
            game = existing.get(record.appid)
            if game is None:
                to_create.append(self._new_game(record))
                fresher.append(record)
                continue
            is_fresher = game.data_date is None or self.data_date >= game.data_date
            touched |= self._apply(game, record, is_fresher)
            to_update.append(game)
            if is_fresher:
                fresher.append(record)
        Game.objects.bulk_create(to_create)
        if to_update and touched:
            Game.objects.bulk_update(to_update, sorted(touched))
        self._save_relations(records)
        self._save_tag_votes(records, fresher)
        self._save_playtimes(fresher)
        self._save_reviews(records)

    def _new_game(self, record: GameRecord) -> Game:
        values = {key: value for key, value in record.fields.items() if not is_empty(value)}
        name = record.name or str(record.appid)
        return Game(appid=record.appid, name=name, data_date=self.data_date, **values)

    def _apply(self, game: Game, record: GameRecord, is_fresher: bool) -> set[str]:
        touched = set()
        values = {"name": record.name, **record.fields}
        for key, value in values.items():
            if is_empty(value) or getattr(game, key) == value:
                continue
            if is_fresher or is_empty(getattr(game, key)) or game.name == str(game.appid):
                setattr(game, key, value)
                touched.add(key)
        if is_fresher and game.data_date != self.data_date:
            game.data_date = self.data_date
            touched.add("data_date")
        return touched

    def _save_relations(self, records: list[GameRecord]) -> None:
        links = (
            (Genre, Game.genres.through, "genre_id", "genres"),
            (Platform, Game.platforms.through, "platform_id", "platforms"),
            (Company, Game.developers.through, "company_id", "developers"),
            (Company, Game.publishers.through, "company_id", "publishers"),
        )
        for entity, through, column, attribute in links:
            pairs = [(r.appid, name) for r in records for name in getattr(r, attribute)]
            ids = ensure_named(entity, {name for _, name in pairs})
            through.objects.bulk_create(
                [
                    through(game_id=appid, **{column: ids[name]})
                    for appid, name in set(pairs)
                    if name in ids
                ],
                ignore_conflicts=True,
            )

    def _save_tag_votes(self, records: list[GameRecord], fresher: list[GameRecord]) -> None:
        ids = ensure_named(Tag, {name for record in records for name in record.tag_votes})
        fresher_appids = {record.appid for record in fresher}
        with_votes, without_votes = [], []
        for record in records:
            for name, votes in record.tag_votes.items():
                if name not in ids:
                    continue
                link = GameTag(game_id=record.appid, tag_id=ids[name], votes=votes)
                if votes and record.appid in fresher_appids:
                    with_votes.append(link)
                else:
                    without_votes.append(link)
        GameTag.objects.bulk_create(
            with_votes,
            update_conflicts=True,
            unique_fields=["game", "tag"],
            update_fields=["votes"],
        )
        GameTag.objects.bulk_create(without_votes, ignore_conflicts=True)

    def _save_playtimes(self, records: list[GameRecord]) -> None:
        playtimes = [
            GamePlaytime(
                game_id=record.appid,
                average_playtime_minutes=record.average_playtime_minutes or 0,
                median_playtime_minutes=record.median_playtime_minutes or 0,
            )
            for record in records
            if record.average_playtime_minutes or record.median_playtime_minutes
        ]
        GamePlaytime.objects.bulk_create(
            playtimes,
            update_conflicts=True,
            unique_fields=["game"],
            update_fields=["average_playtime_minutes", "median_playtime_minutes", "updated_at"],
        )

    def _save_reviews(self, records: list[GameRecord]) -> None:
        reviews = [
            ReviewSummary(
                game_id=record.appid,
                language=self.review_language,
                positive=record.positive_reviews or 0,
                negative=record.negative_reviews or 0,
                date=self.data_date,
            )
            for record in records
            if record.positive_reviews or record.negative_reviews
        ]
        ReviewSummary.objects.bulk_create(
            reviews,
            update_conflicts=True,
            unique_fields=["game", "language", "date"],
            update_fields=["positive", "negative"],
        )


def ensure_named(entity: type[models.Model], names: set[str]) -> dict[str, int]:
    """Crée les noms qui manquent (genres, tags, studios…) et renvoie nom → id."""
    length = NAME_LENGTHS[entity]
    wanted = {name: name.strip()[:length] for name in names if name.strip()}
    entity.objects.bulk_create(
        [entity(name=value) for value in set(wanted.values())], ignore_conflicts=True
    )
    ids = dict(entity.objects.filter(name__in=set(wanted.values())).values_list("name", "id"))
    return {name: ids[value] for name, value in wanted.items()}


def _merge_duplicates(records: tuple[GameRecord, ...]) -> list[GameRecord]:
    """Un même appid deux fois dans un paquet (listes qui se recoupent) : le dernier gagne."""
    return list({record.appid: record for record in records}.values())
