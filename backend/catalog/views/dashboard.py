from datetime import datetime, timedelta, timezone
from decimal import Decimal
from django.db.models import Avg, Count, OuterRef, Subquery, Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game, Genre
from players.models import PlayerCountSnapshot
from pricing.models import PricePoint

DASHBOARD_TOP_LIMIT = 10
SPARKLINE_HOURS = 24


def _build_overview() -> dict:
    total_games = Game.objects.count()
    latest_subquery = (
        PlayerCountSnapshot.objects.filter(game=OuterRef("game"))
        .order_by("-taken_at")
        .values("pk")[:1]
    )
    latest_snaps = PlayerCountSnapshot.objects.filter(pk=Subquery(latest_subquery))
    total_players = latest_snaps.aggregate(total=Sum("players"))["total"] or 0

    top_genre_row = (
        Genre.objects.annotate(games_count=Count("games"))
        .order_by("-games_count", "name")
        .first()
    )
    top_genre = top_genre_row.name if top_genre_row else "Inconnu"

    avg_price_row = PricePoint.objects.filter(price_eur__isnull=False).aggregate(
        avg_price=Avg("price_eur")
    )
    avg_price = (
        float(avg_price_row["avg_price"]) if avg_price_row["avg_price"] is not None else 0.0
    )

    return {
        "games_count": total_games,
        "total_players": total_players,
        "top_genre": top_genre,
        "average_price_eur": round(avg_price, 2),
    }


def _build_top_games() -> list[dict]:
    latest_subquery = (
        PlayerCountSnapshot.objects.filter(game=OuterRef("game"))
        .order_by("-taken_at")
        .values("pk")[:1]
    )
    top_snaps = (
        PlayerCountSnapshot.objects.filter(pk=Subquery(latest_subquery))
        .select_related("game")
        .order_by("-players")[:DASHBOARD_TOP_LIMIT]
    )

    since = datetime.now(timezone.utc) - timedelta(hours=SPARKLINE_HOURS)
    game_ids = [snap.game_id for snap in top_snaps]
    history_rows = (
        PlayerCountSnapshot.objects.filter(game_id__in=game_ids, taken_at__gte=since)
        .order_by("taken_at")
        .values("game_id", "players")
    )
    history_by_game: dict[int, list[int]] = {gid: [] for gid in game_ids}
    for row in history_rows:
        history_by_game[row["game_id"]].append(row["players"])

    return [
        {
            "appid": snap.game.appid,
            "name": snap.game.name,
            "header_image": snap.game.header_image,
            "players": snap.players,
            "sparkline": history_by_game.get(snap.game.appid, [snap.players]),
        }
        for snap in top_snaps
    ]


def _build_featured_gem() -> dict | None:
    gem = (
        Game.objects.filter(
            reviews__positive__gt=0,
            prices__price_eur__gt=0,
            prices__price_eur__lte=Decimal("15.00"),
        )
        .distinct()
        .first()
    )
    if not gem:
        gem = Game.objects.filter(header_image__isnull=False).exclude(header_image="").first()
    if not gem:
        return None
    latest_price = gem.prices.order_by("-date").first()
    return {
        "appid": gem.appid,
        "name": gem.name,
        "header_image": gem.header_image,
        "short_description": gem.short_description,
        "price_eur": float(latest_price.price_eur) if (latest_price and latest_price.price_eur) else 0.0,
    }


@extend_schema(
    responses=inline_serializer(
        "DashboardStats",
        {
            "overview": serializers.DictField(),
            "top_games": serializers.ListField(),
            "featured_gem": serializers.DictField(allow_null=True),
        },
    ),
)
@api_view(["GET"])
def dashboard_stats(request: Request) -> Response:
    """Tableau de bord en direct : chiffres clés, top 10 et sparklines 24h, pépite du jour."""
    return Response(
        {
            "overview": _build_overview(),
            "top_games": _build_top_games(),
            "featured_gem": _build_featured_gem(),
        }
    )
