"""Kaggle « Steam Reviews » (andrewmvd) : 6,4 millions d'avis en anglais, relevés en 2017.

Le fichier pèse ~2 Go : polars le lit en flux et n'en garde que des agrégats par jeu et un
petit échantillon de textes, jamais le fichier entier en mémoire.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import polars as pl

DATASET = "andrewmvd/steam-reviews"
FILENAME = "dataset.csv"
# Le dataset ne date pas les avis : on les range à sa date de collecte.
DATA_DATE = date(2017, 12, 31)
LANGUAGE = "english"
POSITIVE, NEGATIVE = 1, -1
# Les avis jugés utiles, d'une longueur lisible, et pas la mention automatique d'accès anticipé.
MIN_EXCERPT_LENGTH, MAX_EXCERPT_LENGTH = 40, 600
EARLY_ACCESS_MENTION = "Early Access Review"
SCHEMA = {
    "app_id": pl.Int64,
    "app_name": pl.String,
    "review_text": pl.String,
    "review_score": pl.Int64,
    "review_votes": pl.Int64,
}


@dataclass(frozen=True)
class GameReviews:
    appid: int
    name: str
    positive: int
    negative: int


@dataclass(frozen=True)
class Excerpt:
    appid: int
    text: str
    is_positive: bool


def _scan(path: Path, limit: int | None) -> pl.LazyFrame:
    frame = pl.scan_csv(path, schema_overrides=SCHEMA, ignore_errors=True, n_rows=limit)
    return frame.filter(pl.col("app_id").is_not_null())


def read_review_totals(path: Path, limit: int | None = None) -> list[GameReviews]:
    totals = (
        _scan(path, limit)
        .group_by("app_id")
        .agg(
            pl.col("app_name").drop_nulls().first().alias("name"),
            (pl.col("review_score") == POSITIVE).sum().alias("positive"),
            (pl.col("review_score") == NEGATIVE).sum().alias("negative"),
        )
        .sort("app_id")
        .collect(engine="streaming")
    )
    return [
        GameReviews(
            int(row["app_id"]), (row["name"] or "").strip(), row["positive"], row["negative"]
        )
        for row in totals.iter_rows(named=True)
    ]


def read_excerpts(path: Path, per_side: int, limit: int | None = None) -> list[Excerpt]:
    """Jusqu'à `per_side` avis utiles positifs et autant de négatifs par jeu."""
    text = pl.col("review_text").str.strip_chars()
    samples = (
        _scan(path, limit)
        .filter(
            (pl.col("review_votes") == 1)
            & pl.col("review_score").is_in([POSITIVE, NEGATIVE])
            & text.str.len_chars().is_between(MIN_EXCERPT_LENGTH, MAX_EXCERPT_LENGTH)
            & ~text.str.contains(EARLY_ACCESS_MENTION, literal=True)
        )
        .group_by("app_id", "review_score")
        .agg(text.head(per_side).alias("texts"))
        .sort("app_id", "review_score")
        .collect(engine="streaming")
    )
    return [
        Excerpt(int(row["app_id"]), excerpt, row["review_score"] == POSITIVE)
        for row in samples.iter_rows(named=True)
        for excerpt in row["texts"]
    ]
