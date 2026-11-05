from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from geography.models import GoogleTrendsInterest


@extend_schema(
    parameters=[
        OpenApiParameter(name="appid", type=int, required=False, description="Filtrer par Steam AppID"),
        OpenApiParameter(name="genre", type=str, required=False, description="Filtrer par nom de genre"),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def trends_map_stats(request: Request) -> Response:
    """Intérêt Google Trends par pays : `{timeline: [date1, ...], series: {date: {iso3: score}}}`."""
    appid = request.query_params.get("appid")
    genre = request.query_params.get("genre")

    qs = GoogleTrendsInterest.objects.select_related("country", "game")
    if appid and appid.isdigit():
        qs = qs.filter(game_id=int(appid))
    elif genre:
        qs = qs.filter(game__genres__name__iexact=genre)

    dates = sorted({d.isoformat() for d in qs.values_list("date", flat=True).distinct()})
    
    series: dict[str, dict[str, int]] = {d: {} for d in dates}
    for row in qs:
        d_str = row.date.isoformat()
        iso3 = row.country.iso3
        # Si agrégé (ex: plusieurs jeux par genre), on prend le max ou la moyenne
        current = series[d_str].get(iso3, 0)
        series[d_str][iso3] = max(current, row.interest)

    return Response({
        "timeline": dates,
        "series": series,
    })
