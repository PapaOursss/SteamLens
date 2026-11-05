"""Kaggle « Steam Games Dataset » (fronkongames, ~100 000 jeux, mis à jour régulièrement)."""

import re
from pathlib import Path
from typing import Any

import polars as pl

from ingestion.sources.kaggle.cleaning import parse_date, parse_int, parse_money, split_list
from ingestion.sources.kaggle.kaggle_game import KaggleGame
from ingestion.sources.kaggle.usd_price import UsdPrice
from ingestion.writing import GameRecord

DATASET = "fronkongames/steam-games-dataset"
FILENAME = "games.csv"
# L'en-tête du CSV colle « Discount » et « DLC count » : les valeurs, elles, ont bien 40
# colonnes. On remet donc les noms à la main quand on voit ce défaut.
BROKEN_HEADER = "DiscountDLC count"
COLUMNS = (
    "AppID", "Name", "Release date", "Estimated owners", "Peak CCU", "Required age", "Price",
    "Discount", "DLC count", "About the game", "Supported languages", "Full audio languages",
    "Reviews", "Header image", "Website", "Support url", "Support email", "Windows", "Mac",
    "Linux", "Metacritic score", "Metacritic url", "User score", "Positive", "Negative",
    "Score rank", "Achievements", "Recommendations", "Notes", "Average playtime forever",
    "Average playtime two weeks", "Median playtime forever", "Median playtime two weeks",
    "Developers", "Publishers", "Categories", "Genres", "Tags", "Screenshots", "Movies",
)  # fmt: skip
QUOTED = re.compile(r"'([^']+)'")
PLATFORM_COLUMNS = {"Windows": "Windows", "Mac": "macOS", "Linux": "Linux"}
OWNERS_SEPARATOR = "-"


def read_fronkongames(path: Path, limit: int | None = None) -> list[KaggleGame]:
    with path.open(encoding="utf-8") as csv_file:
        header = csv_file.readline()
    if BROKEN_HEADER in header:
        frame = pl.read_csv(
            path, has_header=False, skip_rows=1, new_columns=list(COLUMNS),
            infer_schema=False, n_rows=limit,
        )  # fmt: skip
    else:
        frame = pl.read_csv(path, infer_schema=False, n_rows=limit)
    frame = (
        frame.with_columns(pl.col("AppID").cast(pl.Int64, strict=False).alias("appid"))
        .filter(pl.col("appid").is_not_null())
        .unique("appid", keep="last", maintain_order=True)
    )
    return [_game(row) for row in frame.iter_rows(named=True)]


def _game(row: dict[str, Any]) -> KaggleGame:
    appid = int(row["appid"])
    owners = _owners(row.get("Estimated owners"))
    price = parse_money(row.get("Price"))
    metacritic = parse_int(row.get("Metacritic score"))
    record = GameRecord(
        appid=appid,
        name=(row.get("Name") or "").strip(),
        fields={
            "release_date": parse_date(row.get("Release date")),
            "is_free": None if price is None else price == 0,
            "header_image": (row.get("Header image") or "").strip(),
            "supported_languages": _languages(row.get("Supported languages")),
            "peak_ccu": parse_int(row.get("Peak CCU")),
            "metacritic_score": metacritic or None,
            "categories": split_list(row.get("Categories")),
            "screenshots": split_list(row.get("Screenshots")),
            **owners,
        },
        genres=split_list(row.get("Genres")),
        tag_votes=dict.fromkeys(split_list(row.get("Tags")), 0),
        developers=split_list(row.get("Developers")),
        publishers=split_list(row.get("Publishers")),
        platforms=[name for column, name in PLATFORM_COLUMNS.items() if row.get(column) == "True"],
        average_playtime_minutes=parse_int(row.get("Average playtime forever")) or None,
        median_playtime_minutes=parse_int(row.get("Median playtime forever")) or None,
        positive_reviews=parse_int(row.get("Positive")),
        negative_reviews=parse_int(row.get("Negative")),
    )
    return KaggleGame(record=record, price=UsdPrice(appid, price) if price is not None else None)


def _owners(text: str | None) -> dict[str, int]:
    """« 20000 - 50000 » → min, max, milieu ; rien si illisible."""
    parts = [parse_int(part) for part in (text or "").split(OWNERS_SEPARATOR)]
    if len(parts) != 2 or None in parts:
        return {}
    minimum, maximum = parts
    return {"owners_min": minimum, "owners_max": maximum, "owners_mid": (minimum + maximum) // 2}


def _languages(text: str | None) -> list[str]:
    """« ['English', 'French'] » → liste ; garde les langues utiles aux cartes (T-23)."""
    return [language.strip() for language in QUOTED.findall(text or "") if language.strip()]
