from collections import defaultdict
from typing import Any

from django.db.models import Avg, Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import GameTag, Genre

MAX_TAGS_PER_GENRE = 15


def _build_genre_node(
    genre: Genre,
    tags_by_genre: dict[int, list[dict[str, Any]]],
    genre_totals: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    stats = genre_totals.get(genre.id, {"games": 0, "owners": 0, "score": 0.0})
    return {
        "id": f"genre-{genre.id}",
        "name": genre.name,
        "games": stats["games"],
        "owners": stats["owners"],
        "score": stats["score"],
        "children": tags_by_genre.get(genre.id, []),
    }


def _aggregate_genres() -> dict[int, dict[str, Any]]:
    result = {}
    for r in Genre.objects.filter(games__isnull=False).distinct():
        games_qs = r.games.all()
        games_count = games_qs.count()
        owners = games_qs.aggregate(s=Sum("owners_mid"))["s"] or 0
        score = games_qs.aggregate(a=Avg("metacritic_score"))["a"] or 0.0
        result[r.id] = {
            "games": games_count,
            "owners": owners,
            "score": round(score, 1),
        }
    return result


def _aggregate_genre_tags() -> dict[int, list[dict[str, Any]]]:
    mapping: dict[int, list[dict[str, Any]]] = defaultdict(list)
    data_map: dict[tuple[int, int, str], dict[str, Any]] = defaultdict(
        lambda: {"games": 0, "owners": 0, "scores": [], "votes": 0}
    )
    for row in GameTag.objects.select_related("game", "tag").filter(game__genres__isnull=False):
        for genre in row.game.genres.all():
            key = (genre.id, row.tag.id, row.tag.name)
            data_map[key]["games"] += 1
            data_map[key]["owners"] += row.game.owners_mid or 0
            if row.game.metacritic_score is not None:
                data_map[key]["scores"].append(row.game.metacritic_score)
            data_map[key]["votes"] += row.votes

    for (genre_id, tag_id, tag_name), stat in data_map.items():
        avg_score = (
            round(sum(stat["scores"]) / len(stat["scores"]), 1)
            if stat["scores"]
            else 0.0
        )
        mapping[genre_id].append(
            {
                "id": f"tag-{genre_id}-{tag_id}",
                "name": tag_name,
                "games": stat["games"],
                "owners": stat["owners"],
                "score": avg_score,
                "votes": stat["votes"],
            }
        )

    for genre_id, tags in list(mapping.items()):
        tags.sort(key=lambda item: item["games"], reverse=True)
        mapping[genre_id] = tags[:MAX_TAGS_PER_GENRE]

    return mapping


@extend_schema(
    responses=inline_serializer(
        "TreemapResponse",
        {
            "name": serializers.CharField(),
            "children": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def genre_tags_treemap(request: Request) -> Response:
    """Hiérarchie Genre -> Tags pour le treemap (T-15)."""
    genre_totals = _aggregate_genres()
    tags_by_genre = _aggregate_genre_tags()

    genres = Genre.objects.filter(id__in=genre_totals.keys()).order_by("name")
    nodes = [_build_genre_node(g, tags_by_genre, genre_totals) for g in genres]

    return Response(
        {
            "name": "Steam",
            "children": nodes,
        }
    )
