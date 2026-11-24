from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.release_calendar import build_release_calendar_stats


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="year",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Année pour le calendrier quotidien de sorties",
            required=False,
        ),
    ],
    responses=inline_serializer(
        "ReleaseCalendarResponse",
        {
            "is_sample": serializers.BooleanField(),
            "weekday_month": serializers.ListField(
                child=serializers.ListField(child=serializers.IntegerField())
            ),
            "daily_contributions": serializers.ListField(child=serializers.ListField()),
            "selected_year": serializers.IntegerField(),
            "available_years": serializers.ListField(child=serializers.IntegerField()),
            "days": serializers.ListField(child=serializers.CharField()),
            "months": serializers.ListField(child=serializers.CharField()),
        },
    ),
)
@api_view(["GET"])
def release_calendar_stats(request: Request) -> Response:
    """Statistiques de calendrier des sorties : heatmap jour x mois et calendrier quotidien."""
    year_param = request.query_params.get("year")
    year = int(year_param) if (year_param and year_param.isdigit()) else None
    data = build_release_calendar_stats(year=year)
    return Response(data)
