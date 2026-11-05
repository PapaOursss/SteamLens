from dataclasses import asdict

from django.db.models import Max
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game, ReviewSummary
from catalog.review_bombing import SHARE_DECIMALS, find_bombings, positive_share

MAX_BOMBED_GAMES = 20


def _language_rows(game: Game) -> list[dict]:
    """Totaux par langue de la dernière photo des avis du jeu."""
    latest = game.reviews.aggregate(day=Max("date"))["day"]
    summaries = ReviewSummary.objects.filter(game=game, date=latest).order_by("language")
    return [
        {
            "language": summary.language,
            "positive": summary.positive,
            "negative": summary.negative,
            "positive_share": round(summary.positive / summary.total, SHARE_DECIMALS),
        }
        for summary in summaries
        if summary.total
    ]


@extend_schema(
    responses=inline_serializer(
        "GameReviews",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "languages": serializers.ListField(child=serializers.DictField()),
            "weeks": serializers.ListField(child=serializers.DictField()),
            "bombings": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def game_reviews(request: Request, appid: int) -> Response:
    """Avis d'un jeu : ratio positif par langue, courbe par semaine et review bombings."""
    game = get_object_or_404(Game, appid=appid)
    weeks = list(game.review_weeks.all())
    return Response(
        {
            "appid": game.appid,
            "name": game.name,
            "languages": _language_rows(game),
            "weeks": [
                {
                    "week_start": week.week_start,
                    "positive": week.positive,
                    "negative": week.negative,
                    "positive_share": round(positive_share(week), SHARE_DECIMALS),
                }
                for week in weeks
            ],
            "bombings": [asdict(bombing) for bombing in find_bombings(weeks)],
        }
    )


@extend_schema(
    responses=inline_serializer(
        "ReviewBombing",
        {
            "appid": serializers.IntegerField(),
            "name": serializers.CharField(),
            "week_start": serializers.DateField(),
            "positive_share": serializers.FloatField(),
            "baseline_share": serializers.FloatField(),
            "drop": serializers.FloatField(),
            "reviews": serializers.IntegerField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def review_bombings(request: Request) -> Response:
    """Les plus fortes chutes de ratio positif repérées, tous jeux confondus."""
    games = Game.objects.filter(review_weeks__isnull=False).distinct()
    found = [
        {"appid": game.appid, "name": game.name, **asdict(bombing)}
        for game in games.prefetch_related("review_weeks")
        for bombing in find_bombings(list(game.review_weeks.all()))
    ]
    found.sort(key=lambda row: row["drop"], reverse=True)
    return Response(found[:MAX_BOMBED_GAMES])
