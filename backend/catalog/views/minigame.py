import random

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game
from players.models import PlayerCountSnapshot
from pricing.models import PricePoint


def _get_player_count(game: Game) -> int:
    snap = PlayerCountSnapshot.objects.filter(game=game).order_by("-taken_at").first()
    return snap.players if snap else 0


def _get_price_eur(game: Game) -> float:
    price_pt = PricePoint.objects.filter(game=game).order_by("-date").first()
    if price_pt and price_pt.price_eur is not None:
        return float(price_pt.price_eur)
    return 0.0 if game.is_free else 19.99


def _get_review_score(game: Game) -> int:
    review = game.reviews.first()
    if review and review.total > 0:
        return int((review.positive / review.total) * 100)
    return 75


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

    games = list(Game.objects.all()[:50])
    if len(games) < 2:
        game_a, game_b = _generate_fallback_pair()
    else:
        sample = random.sample(games, 2)
        game_a, game_b = _serialize_card(sample[0]), _serialize_card(sample[1])

    return Response({
        "game_a": game_a,
        "game_b": game_b,
        "metric": metric,
    })
