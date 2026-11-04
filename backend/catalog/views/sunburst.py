from collections import defaultdict
from typing import Any

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game


def _build_mode_node(mode_name: str, games_count: int, owners_count: int) -> dict[str, Any]:
    return {"name": mode_name, "value": games_count, "games": games_count, "owners": owners_count}


def _build_theme_node(
    theme_name: str, modes: dict[str, dict[str, int]]
) -> dict[str, Any]:
    children = [
        _build_mode_node(m_name, counts["games"], counts["owners"])
        for m_name, counts in modes.items()
    ]
    total_games = sum(c["games"] for c in children)
    total_owners = sum(c["owners"] for c in children)
    return {
        "name": theme_name,
        "value": total_games,
        "games": total_games,
        "owners": total_owners,
        "children": sorted(children, key=lambda c: c["games"], reverse=True),
    }


def _build_genre_node(
    genre_name: str, themes: dict[str, dict[str, dict[str, int]]]
) -> dict[str, Any]:
    children = [_build_theme_node(t_name, modes) for t_name, modes in themes.items()]
    total_games = sum(c["games"] for c in children)
    total_owners = sum(c["owners"] for c in children)
    return {
        "name": genre_name,
        "value": total_games,
        "games": total_games,
        "owners": total_owners,
        "children": sorted(children, key=lambda c: c["games"], reverse=True),
    }


def _collect_hierarchy() -> dict[str, dict[str, dict[str, dict[str, int]]]]:
    hierarchy: dict[str, dict[str, dict[str, dict[str, int]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: {"games": 0, "owners": 0}))
    )
    games = Game.objects.prefetch_related("igdb_genres", "themes", "game_modes").filter(
        igdb_genres__isnull=False
    )
    for game in games:
        genres = [g.name for g in game.igdb_genres.all()]
        themes = [t.name for t in game.themes.all()] or ["Non spécifié"]
        modes = [m.name for m in game.game_modes.all()] or ["Standard"]
        owners = game.owners_mid or 0

        for g in genres:
            for t in themes:
                for m in modes:
                    hierarchy[g][t][m]["games"] += 1
                    hierarchy[g][t][m]["owners"] += owners
    return hierarchy


@extend_schema(
    responses=inline_serializer(
        "SunburstResponse",
        {
            "name": serializers.CharField(),
            "children": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def sunburst_igdb(request: Request) -> Response:
    """Hiérarchie IGDB Genre -> Thème -> Mode de jeu pour sunburst (T-15)."""
    hierarchy = _collect_hierarchy()
    genres_nodes = [
        _build_genre_node(g_name, themes)
        for g_name, themes in sorted(hierarchy.items(), key=lambda x: x[0])
    ]
    return Response(
        {
            "name": "IGDB",
            "children": sorted(genres_nodes, key=lambda n: n["games"], reverse=True),
        }
    )
