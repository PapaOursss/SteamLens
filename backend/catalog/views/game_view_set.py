from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from catalog.filters import GameFilter
from catalog.models import Game
from catalog.serializers import GameDetailSerializer, GameListSerializer
from players.serializers import PlayerCountSerializer
from pricing.serializers import PricePointSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """`/api/games/` (liste paginée et filtrée), `/api/games/<appid>/` et ses courbes."""

    filterset_class = GameFilter
    lookup_field = "appid"

    def get_queryset(self) -> QuerySet[Game]:
        games = Game.objects.prefetch_related("genres")
        if self.action == "retrieve":
            games = games.prefetch_related(
                "game_tags__tag", "themes", "game_modes", "platforms", "developers", "publishers"
            )
        return games.distinct()

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "retrieve":
            return GameDetailSerializer
        return GameListSerializer

    @extend_schema(responses=PlayerCountSerializer(many=True))
    @action(detail=True, pagination_class=None, filterset_class=None)
    def players(self, request: Request, appid: str) -> Response:
        """Joueurs connectés au fil du temps, du plus ancien au plus récent."""
        snapshots = self.get_object().player_counts.order_by("taken_at")
        return Response(PlayerCountSerializer(snapshots, many=True).data)

    @extend_schema(
        parameters=[OpenApiParameter("country", OpenApiTypes.STR)],
        responses=PricePointSerializer(many=True),
    )
    @action(detail=True, pagination_class=None, filterset_class=None)
    def prices(self, request: Request, appid: str) -> Response:
        """Historique des prix ; `?country=FR` pour un seul pays."""
        prices = self.get_object().prices.order_by("date")
        country = request.query_params.get("country")
        if country:
            prices = prices.filter(country_id=country.upper())
        return Response(PricePointSerializer(prices, many=True).data)
