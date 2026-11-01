"""Kaggle « Steam Games Complete Dataset » (trolukovich, ~40 000 jeux relevés en 2019)."""

import re
from pathlib import Path
from typing import Any

import polars as pl

from ingestion.sources.kaggle.cleaning import parse_date, parse_money, split_list
from ingestion.sources.kaggle.kaggle_game import KaggleGame
from ingestion.sources.kaggle.usd_price import UsdPrice
from ingestion.writing import GameRecord

DATASET = "trolukovich/steam-games-complete-dataset"
FILENAME = "steam_games.csv"
APPID_IN_URL = r"store\.steampowered\.com/app/(\d+)"
# « Very Positive,(42,550),- 92% of the 42,550 user reviews for this game are positive. »
REVIEWS = re.compile(r"(\d+)% of the ([\d,]+) user reviews")
HUNDRED = 100


def read_steam_complete(path: Path, limit: int | None = None) -> list[KaggleGame]:
    """Lit le CSV : appid tiré de l'URL, lots et bundles écartés, un seul jeu par appid."""
    frame = pl.read_csv(path, infer_schema=False, n_rows=limit)
    if "types" in frame.columns:
        frame = frame.filter(pl.col("types").is_null() | (pl.col("types") == "app"))
    frame = (
        frame.with_columns(
            pl.col("url").str.extract(APPID_IN_URL, 1).cast(pl.Int64, strict=False).alias("appid")
        )
        .filter(pl.col("appid").is_not_null())
        .unique("appid", keep="last", maintain_order=True)
    )
    return [_game(row) for row in frame.iter_rows(named=True)]


def _game(row: dict[str, Any]) -> KaggleGame:
    appid = int(row["appid"])
    initial = parse_money(row.get("original_price"))
    discounted = parse_money(row.get("discount_price"))
    final = discounted if discounted is not None else initial
    positive, negative = _reviews(row.get("all_reviews"))
    record = GameRecord(
        appid=appid,
        name=(row.get("name") or "").strip(),
        fields={
            "release_date": parse_date(row.get("release_date")),
            "is_free": None if initial is None else initial == 0,
            "short_description": (row.get("desc_snippet") or "").strip(),
            "supported_languages": split_list(row.get("languages")),
            "categories": split_list(row.get("game_details")),
        },
        genres=split_list(row.get("genre")),
        tag_votes=dict.fromkeys(split_list(row.get("popular_tags")), 0),
        developers=split_list(row.get("developer")),
        publishers=split_list(row.get("publisher")),
        positive_reviews=positive,
        negative_reviews=negative,
    )
    price = UsdPrice(appid, final, initial) if final is not None else None
    return KaggleGame(record=record, price=price)


def _reviews(text: str | None) -> tuple[int | None, int | None]:
    match = REVIEWS.search(text or "")
    if match is None:
        return None, None
    total = int(match.group(2).replace(",", ""))
    positive = round(total * int(match.group(1)) / HUNDRED)
    return positive, total - positive
