from django.db.models import F
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game, ReviewSummary
from ingestion.writing.game_writer import ALL_LANGUAGES

PERCENT = 100
MAX_ITEMS = 300


@extend_schema(
    responses=inline_serializer(
        "RatingComparisonPoint",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "steam_score": serializers.FloatField(),
            "press_score": serializers.IntegerField(),
            "rawg_rating": serializers.FloatField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def rating_comparison(request: Request) -> Response:
    """Nuage de points : Note presse (Metacritic) vs Note Steam (%) avec accord sur la diagonale."""
    games = (
        Game.objects.filter(
            metacritic_score__isnull=False,
            metacritic_score__gt=0,
            reviews__language=ALL_LANGUAGES,
        )
        .annotate(
            rev_pos=F("reviews__positive"),
            rev_neg=F("reviews__negative"),
        )
        .values("appid", "name", "metacritic_score", "rawg_rating", "rev_pos", "rev_neg")
        .distinct()[:MAX_ITEMS]
    )

    points = []
    for g in games:
        total = (g["rev_pos"] or 0) + (g["rev_neg"] or 0)
        if total < 10:
            continue
        steam_score = round(((g["rev_pos"] or 0) * PERCENT) / total, 1)
        points.append(
            {
                "appid": g["appid"],
                "name": g["name"],
                "steam_score": steam_score,
                "press_score": g["metacritic_score"],
                "rawg_rating": g["rawg_rating"],
            }
        )

    return Response(points)
