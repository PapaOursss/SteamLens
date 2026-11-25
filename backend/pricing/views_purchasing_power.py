from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game
from pricing.purchasing_power import purchasing_power


@extend_schema(
    parameters=[OpenApiParameter("appid", int, description="jeu ; sans lui, 60 € partout")],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def purchasing_power_stats(request: Request) -> Response:
    """Carte n°4 : heures de travail que coûte un jeu, au prix régional et au prix américain."""
    appid = request.query_params.get("appid")
    if appid and not appid.isdigit():
        return Response({"detail": "appid invalide."}, status=status.HTTP_400_BAD_REQUEST)
    game = get_object_or_404(Game, appid=appid) if appid else None
    return Response(purchasing_power(game))
