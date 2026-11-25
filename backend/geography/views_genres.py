from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from geography.genre_taste import genres_by_country


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def genres_by_country_stats(request: Request) -> Response:
    """Carte n°2 : genre le plus surreprésenté par pays, d'après la langue des avis (T-23)."""
    return Response(genres_by_country())
