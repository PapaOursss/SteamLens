import random
from itertools import islice

from django.db.models import F
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game
from players.models import PlayerCountSnapshot
from pricing.models import PricePoint

FRANCE_ISO2 = "FR"
POOL_SIZE = 200


def _get_player_count(game: Game) -> int:
    snap = PlayerCountSnapshot.objects.filter(game=game).order_by("-taken_at").first()
    return snap.players if snap else 0


def _get_price_eur(game: Game) -> float:
    price_pt = (
        PricePoint.objects.filter(game=game, country=FRANCE_ISO2, price_eur__isnull=False)
        .order_by("-date")
        .first()
    )
    return float(price_pt.price_eur) if price_pt else 0.0


def _get_review_score(game: Game) -> int:
    review = game.reviews.filter(language="all").order_by("-date").first()
    if review and review.total > 0:
        return int((review.positive / review.total) * 100)
    return 0


def _has_value(game: Game, metric: str) -> bool:
    """Un jeu sans relevé ne se joue pas ; un prix de 0 n'est vrai que pour un jeu gratuit."""
    if metric == "players":
        return _get_player_count(game) > 0
    if metric == "price_eur":
        return game.is_free or _get_price_eur(game) > 0
    return _get_review_score(game) > 0


def _draw_pair(metric: str) -> list[Game]:
    games = list(Game.objects.order_by(F("owners_mid").desc(nulls_last=True))[:POOL_SIZE])
    random.shuffle(games)
    return list(islice((game for game in games if _has_value(game, metric)), 2))


def _serialize_card(game: Game) -> dict:
    return {
        "appid": game.appid,
        "name": game.name,
        "header_image": game.header_image,
        "players": _get_player_count(game),
        "price_eur": _get_price_eur(game),
        "review_score": _get_review_score(game),
    }


def _generate_fallback_pair() -> tuple[dict, dict]:
    game_a = {
        "appid": 730,
        "name": "Counter-Strike 2",
        "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg",
        "players": 1250000,
        "price_eur": 0.0,
        "review_score": 88,
    }
    game_b = {
        "appid": 570,
        "name": "Dota 2",
        "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/570/header.jpg",
        "players": 650000,
        "price_eur": 0.0,
        "review_score": 82,
    }
    return game_a, game_b


@extend_schema(
    responses=inline_serializer(
        "GameDuel",
        {
            "game_a": serializers.DictField(),
            "game_b": serializers.DictField(),
            "metric": serializers.CharField(),
        },
    ),
)
@api_view(["GET"])
def game_duel(request: Request) -> Response:
    """Fournit deux jeux et une métrique (players, price_eur, review_score) pour le mini-jeu Plus ou Moins."""
    metrics = ["players", "price_eur", "review_score"]
    metric = request.query_params.get("metric")
    if metric not in metrics:
        metric = random.choice(metrics)

    games = _draw_pair(metric)
    if len(games) < 2:
        game_a, game_b = _generate_fallback_pair()
    else:
        game_a, game_b = _serialize_card(games[0]), _serialize_card(games[1])

    return Response(
        {
            "game_a": game_a,
            "game_b": game_b,
            "metric": metric,
        }
    )
