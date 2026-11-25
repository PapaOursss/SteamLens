from django.db.models import QuerySet
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from catalog.filters import GameFilter
from catalog.game_dna import game_dna
from catalog.models import Game
from catalog.serializers import GameDetailSerializer, GameListSerializer
from catalog.similar_games import similar_games
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

    @extend_schema(
        responses=inline_serializer(
            "GameDnaAxis",
            {
                "key": serializers.CharField(),
                "score": serializers.IntegerField(allow_null=True),
                "raw": serializers.FloatField(allow_null=True),
            },
            many=True,
        )
    )
    @action(detail=True, pagination_class=None, filterset_class=None)
    def dna(self, request: Request, appid: str) -> Response:
        """« ADN du jeu » : chaque axe rangé de 0 à 100 parmi les jeux mesurés, None sans donnée."""
        return Response(game_dna(self.get_object()))

    @extend_schema(
        responses=inline_serializer(
            "SimilarGame",
            {
                "appid": serializers.IntegerField(),
                "name": serializers.CharField(),
                "header_image": serializers.CharField(),
                "score": serializers.FloatField(),
                "shared_tags": serializers.ListField(child=serializers.CharField()),
            },
            many=True,
        )
    )
    @action(detail=True, pagination_class=None, filterset_class=None)
    def similar(self, request: Request, appid: str) -> Response:
        """Les 10 jeux aux tags les plus proches (cosinus), précalculés par compute_similar_games."""
        return Response(similar_games(self.get_object()))
