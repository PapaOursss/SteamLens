from django.db.models import OuterRef, Subquery
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from players.models import PlayerCountSnapshot

DEFAULT_TOP_PLAYED_LIMIT = 10
MAX_TOP_PLAYED_LIMIT = 100


@extend_schema(
    parameters=[OpenApiParameter("limit", OpenApiTypes.INT)],
    responses=inline_serializer(
        "TopPlayedGame",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "header_image": serializers.URLField(),
            "players": serializers.IntegerField(),
            "taken_at": serializers.DateTimeField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def top_played(request: Request) -> Response:
    """Les jeux les plus joués d'après la dernière photo de chacun ; `?limit=` (10 par défaut)."""
    limit = _read_limit(request.query_params.get("limit"))
    latest_per_game = (
        PlayerCountSnapshot.objects.filter(game=OuterRef("game"))
        .order_by("-taken_at")
        .values("pk")[:1]
    )
    snapshots = (
        PlayerCountSnapshot.objects.filter(pk=Subquery(latest_per_game))
        .select_related("game")
        .order_by("-players")[:limit]
    )
    return Response(
        [
            {
                "appid": snapshot.game.appid,
                "name": snapshot.game.name,
                "header_image": snapshot.game.header_image,
                "players": snapshot.players,
                "taken_at": snapshot.taken_at,
            }
            for snapshot in snapshots
        ]
    )


def _read_limit(raw_limit: str | None) -> int:
    if raw_limit is None or not raw_limit.isdigit():
        return DEFAULT_TOP_PLAYED_LIMIT
    return max(1, min(int(raw_limit), MAX_TOP_PLAYED_LIMIT))
