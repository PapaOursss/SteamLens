from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.achievement_curve import abandon_curve, biggest_drop, completion_rate, median_percent
from catalog.models import Game

RANKING_SIZE = 20


@extend_schema(
    responses=inline_serializer(
        "GameAchievements",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "completion_rate": serializers.FloatField(allow_null=True),
            "biggest_drop": serializers.DictField(allow_null=True),
            "curve": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def game_achievements(request: Request, appid: int) -> Response:
    """Courbe d'abandon d'un jeu : ses succès triés par rareté."""
    game = get_object_or_404(Game, appid=appid)
    achievements = list(game.achievements.all())
    curve = abandon_curve(achievements)
    return Response(
        {
            "appid": game.appid,
            "name": game.name,
            "completion_rate": completion_rate(achievements),
            "biggest_drop": biggest_drop(curve),
            "curve": curve,
        }
    )


@extend_schema(
    responses=inline_serializer(
        "LeastFinishedGame",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "header_image": serializers.CharField(),
            "completion_rate": serializers.FloatField(),
            "median_percent": serializers.FloatField(),
            "achievements": serializers.IntegerField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def least_finished_games(request: Request) -> Response:
    """Jeux au plus faible taux de fin, d'après leur succès de fin d'histoire."""
    games = Game.objects.filter(achievements__isnull=False).distinct()
    ranking = []
    for game in games.prefetch_related("achievements"):
        achievements = list(game.achievements.all())
        rate = completion_rate(achievements)
        if rate is not None:
            ranking.append(
                {
                    "appid": game.appid,
                    "name": game.name,
                    "header_image": game.header_image,
                    "completion_rate": rate,
                    "median_percent": median_percent(achievements),
                    "achievements": len(achievements),
                }
            )
    ranking.sort(key=lambda row: row["completion_rate"])
    return Response(ranking[:RANKING_SIZE])
