from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game


def _build_game_hype_item(game: Game) -> dict:
    t_snap = game.twitch_snapshots.first()
    p_snap = game.player_counts.order_by("-taken_at").first()
    viewers = t_snap.viewer_count if t_snap else 0
    players = p_snap.players if p_snap else 0
    ratio = round(viewers / players, 2) if players > 0 else 0.0

    return {
        "appid": game.appid,
        "name": game.name,
        "header_image": game.header_image,
        "viewers": viewers,
        "players": players,
        "hype_ratio": ratio,
    }


def _mock_hype_stats() -> dict:
    watched_more = [
        {
            "appid": 252490,
            "name": "Rust",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/252490/header.jpg",
            "viewers": 140000,
            "players": 65000,
            "hype_ratio": 2.15,
        },
        {
            "appid": 1086940,
            "name": "Baldur's Gate 3",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/1086940/header.jpg",
            "viewers": 95000,
            "players": 55000,
            "hype_ratio": 1.73,
        },
    ]
    played_in_silence = [
        {
            "appid": 413150,
            "name": "Stardew Valley",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg",
            "viewers": 3500,
            "players": 85000,
            "hype_ratio": 0.04,
        },
        {
            "appid": 289070,
            "name": "Civilization VI",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/289070/header.jpg",
            "viewers": 1200,
            "players": 52000,
            "hype_ratio": 0.02,
        },
    ]
    return {"watched_more": watched_more, "played_in_silence": played_in_silence}


@extend_schema(
    responses=inline_serializer(
        "HypeStats",
        {
            "watched_more": serializers.ListField(child=serializers.DictField()),
            "played_in_silence": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def hype_stats(request: Request) -> Response:
    """Analyse Twitch vs Steam : ratio spectateurs / joueurs et classement des extrêmes."""
    games = (
        Game.objects.filter(twitch_snapshots__isnull=False, player_counts__isnull=False)
        .prefetch_related("twitch_snapshots", "player_counts")
        .distinct()[:50]
    )
    if not games:
        return Response(_mock_hype_stats())

    all_stats = [_build_game_hype_item(g) for g in games if _build_game_hype_item(g)["players"] > 0]
    if not all_stats:
        return Response(_mock_hype_stats())

    watched_more = sorted(all_stats, key=lambda x: x["hype_ratio"], reverse=True)[:5]
    played_in_silence = sorted(all_stats, key=lambda x: x["hype_ratio"])[:5]

    return Response({
        "watched_more": watched_more,
        "played_in_silence": played_in_silence,
    })
