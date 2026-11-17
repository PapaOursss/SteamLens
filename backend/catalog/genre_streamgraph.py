from collections import defaultdict
from typing import Any

from django.db.models import Count
from django.db.models.functions import ExtractYear

from catalog.models import Game

TOP_GENRES_LIMIT = 8

KEY_EVENTS = [
    {
        "year": 2012,
        "title": "Steam Greenlight",
        "description": "Lancement de Steam Greenlight ouvrant la plateforme aux créateurs indépendants.",
    },
    {
        "year": 2015,
        "title": "Explosion indé & survie",
        "description": "Engouement massif pour les jeux indés, roguelikes et jeux de survie en accès anticipé.",
    },
    {
        "year": 2017,
        "title": "Steam Direct",
        "description": "Remplacement de Greenlight par Steam Direct : accélération majeure des sorties de jeux.",
    },
]


def build_genre_streamgraph() -> dict[str, Any]:
    """Calcule le volume annuel de sorties par genre et les événements clés."""
    top_genres_qs = (
        Game.objects.filter(release_date__isnull=False, genres__isnull=False)
        .values("genres__name")
        .annotate(total=Count("appid", distinct=True))
        .order_by("-total")[:TOP_GENRES_LIMIT]
    )
    top_genres = [item["genres__name"] for item in top_genres_qs if item["genres__name"]]

    if not top_genres:
        return {"years": [], "genres": [], "series": [], "events": KEY_EVENTS}

    aggregates = (
        Game.objects.filter(
            release_date__isnull=False,
            genres__name__in=top_genres,
        )
        .annotate(year=ExtractYear("release_date"))
        .values("year", "genres__name")
        .annotate(count=Count("appid", distinct=True))
    )

    data_map: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    all_years: set[int] = set()

    for row in aggregates:
        year = row["year"]
        genre = row["genres__name"]
        cnt = row["count"]
        if year is not None:
            data_map[genre][year] = cnt
            all_years.add(year)

    sorted_years = sorted(all_years) if all_years else []
    matrix = [[data_map[genre][year] for year in sorted_years] for genre in top_genres]

    return {
        "years": sorted_years,
        "genres": top_genres,
        "series": matrix,
        "events": KEY_EVENTS,
    }
