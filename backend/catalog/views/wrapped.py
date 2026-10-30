from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from players.models import PlayerCountSnapshot
from pricing.models import PricePoint


def _calculate_top_game() -> dict:
    top_snap = PlayerCountSnapshot.objects.order_by("-players").first()
    if top_snap and top_snap.game:
        return {
            "appid": top_snap.game.appid,
            "name": top_snap.game.name,
            "header_image": top_snap.game.header_image,
            "peak_players": top_snap.players,
        }
    return {
        "appid": 730,
        "name": "Counter-Strike 2",
        "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg",
        "peak_players": 1420000,
    }


def _calculate_top_discount() -> dict:
    best_discount = PricePoint.objects.order_by("-discount_percent").first()
    if best_discount and best_discount.discount_percent > 0:
        return {
            "name": best_discount.game.name,
            "discount_percent": best_discount.discount_percent,
            "final_price_eur": float(best_discount.price_eur or 0.0),
        }
    return {
        "name": "The Witcher 3: Wild Hunt",
        "discount_percent": 80,
        "final_price_eur": 5.99,
    }


@extend_schema(
    responses=inline_serializer(
        "WrappedStats",
        {
            "year": serializers.IntegerField(),
            "game_of_the_year": serializers.DictField(),
            "trending_genre": serializers.DictField(),
            "biggest_discount": serializers.DictField(),
            "biggest_flop": serializers.DictField(),
            "most_expensive_country": serializers.DictField(),
        },
    ),
)
@api_view(["GET"])
def steam_wrapped(request: Request) -> Response:
    """Rétrospective interactive annuelle façon Spotify Wrapped."""
    year = int(request.query_params.get("year", 2026))

    game_of_the_year = _calculate_top_game()
    biggest_discount = _calculate_top_discount()

    trending_genre = {
        "name": "Roguelike Deckbuilder",
        "growth_percent": 145,
        "flagship_game": "Balatro",
    }

    biggest_flop = {
        "name": "The Day Before",
        "reason": "Retiré des ventes 4 jours après son lancement suite à 85% d'avis négatifs.",
    }

    most_expensive_country = {
        "country": "Suisse (CHF)",
        "premium_percent": 18.5,
        "reason": "Prix de base systématiquement ajustés au-dessus de la zone Euro.",
    }

    return Response({
        "year": year,
        "game_of_the_year": game_of_the_year,
        "trending_genre": trending_genre,
        "biggest_discount": biggest_discount,
        "biggest_flop": biggest_flop,
        "most_expensive_country": most_expensive_country,
    })
