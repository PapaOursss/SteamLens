from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from geography.map_indicators import MAP_INDICATORS


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def world_map(request: Request, indicator: str) -> Response:
    """`/api/map/<indicateur>/` : `{iso3: valeur}` pour colorier une carte du monde."""
    compute = MAP_INDICATORS.get(indicator)
    if compute is None:
        known = ", ".join(sorted(MAP_INDICATORS))
        raise NotFound(f"Indicateur inconnu : {indicator}. Disponibles : {known}.")
    return Response(compute())
