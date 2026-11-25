"""Kaggle « Top games on Twitch 2016 - 2023 » (rankirsh) : le top 200 de chaque mois.

Relevés SullyGnome de janvier 2016 à septembre 2024 : heures regardées, spectateurs moyens et
au pic, nombre de streamers. Il comble le passé que l'API Helix ne donne pas.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import polars as pl

DATASET = "rankirsh/evolution-of-top-games-on-twitch"
FILENAME = "Twitch_game_data.csv"
SCHEMA = {
    "Rank": pl.Int32,
    "Game": pl.String,
    "Month": pl.Int32,
    "Year": pl.Int32,
    "Hours_watched": pl.Int64,
    "Peak_viewers": pl.Int64,
    "Streamers": pl.Int64,
    "Avg_viewers": pl.Int64,
}


@dataclass(frozen=True)
class TwitchMonthRow:
    name: str
    month: date
    rank: int
    hours_watched: int
    avg_viewers: int
    peak_viewers: int
    streamers: int


def read_history(path: Path, limit: int | None = None) -> list[TwitchMonthRow]:
    """Une ligne par jeu et par mois ; un même nom deux fois dans un mois garde le mieux classé."""
    frame = (
        pl.scan_csv(path, schema_overrides=SCHEMA, n_rows=limit, encoding="utf8-lossy")
        .select(SCHEMA.keys())
        .filter(pl.col("Game").is_not_null() & pl.col("Year").is_not_null())
        .with_columns(pl.col("Game").str.strip_chars())
        .filter(pl.col("Game") != "")
        .sort("Rank")
        .unique(subset=["Game", "Year", "Month"], keep="first", maintain_order=True)
        .collect()
    )
    return [
        TwitchMonthRow(
            name=row["Game"],
            month=date(row["Year"], row["Month"], 1),
            rank=row["Rank"],
            hours_watched=row["Hours_watched"] or 0,
            avg_viewers=row["Avg_viewers"] or 0,
            peak_viewers=row["Peak_viewers"] or 0,
            streamers=row["Streamers"] or 0,
        )
        for row in frame.iter_rows(named=True)
    ]
