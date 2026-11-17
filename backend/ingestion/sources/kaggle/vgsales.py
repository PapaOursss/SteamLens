"""Kaggle « Video Game Sales » (gregorut) : 16 600 jeux vendus à plus de 100 000 exemplaires.

Ventes en millions d'unités, toutes plateformes (consoles comprises), relevées sur VGChartz
jusqu'en 2016 : la seule source gratuite qui sépare Amérique du Nord, Europe, Japon et reste
du monde.
"""

from dataclasses import dataclass
from pathlib import Path

import polars as pl

DATASET = "gregorut/videogamesales"
FILENAME = "vgsales.csv"
SCHEMA = {
    "Name": pl.String,
    "Platform": pl.String,
    "Year": pl.String,
    "Genre": pl.String,
    "Publisher": pl.String,
    "NA_Sales": pl.Float64,
    "EU_Sales": pl.Float64,
    "JP_Sales": pl.Float64,
    "Other_Sales": pl.Float64,
}


@dataclass(frozen=True)
class GameSales:
    name: str
    platform: str
    year: int | None
    genre: str
    publisher: str
    na: float
    eu: float
    jp: float
    other: float


def read_sales(path: Path, limit: int | None = None) -> list[GameSales]:
    """Une ligne par jeu et par plateforme ; l'année « N/A » devient None."""
    frame = (
        pl.scan_csv(path, schema_overrides=SCHEMA, n_rows=limit)
        .filter(pl.col("Name").is_not_null() & pl.col("Genre").is_not_null())
        .with_columns(pl.col("Year").cast(pl.Int16, strict=False))
        .collect()
    )
    return [
        GameSales(
            name=row["Name"].strip(),
            platform=row["Platform"] or "",
            year=row["Year"],
            genre=row["Genre"].strip(),
            publisher=row["Publisher"] or "",
            na=row["NA_Sales"] or 0.0,
            eu=row["EU_Sales"] or 0.0,
            jp=row["JP_Sales"] or 0.0,
            other=row["Other_Sales"] or 0.0,
        )
        for row in frame.iter_rows(named=True)
    ]
