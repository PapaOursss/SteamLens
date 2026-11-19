from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.gem_finder import build_gem_finder_data


@extend_schema(
    responses=inline_serializer(
        "GemFinderResponse",
        {
            "games": serializers.ListField(
                child=inline_serializer(
                    "GemFinderGame",
                    {
                        "appid": serializers.IntegerField(),
                        "name": serializers.CharField(),
                        "header_image": serializers.CharField(),
                        "price_eur": serializers.FloatField(),
                        "positive_percent": serializers.IntegerField(),
                        "owners": serializers.IntegerField(),
                        "genre": serializers.CharField(),
                        "year": serializers.IntegerField(allow_null=True),
                        "is_gem": serializers.BooleanField(),
                    },
                )
            ),
            "genres": serializers.ListField(child=serializers.CharField()),
            "years": serializers.ListField(child=serializers.IntegerField()),
            "gem_criteria": inline_serializer(
                "GemCriteria",
                {
                    "max_price": serializers.FloatField(),
                    "min_score": serializers.IntegerField(),
                    "max_owners": serializers.IntegerField(),
                },
            ),
        },
    ),
)
@api_view(["GET"])
def gem_finder(request: Request) -> Response:
    """Données pour le nuage de points 'chercheur de pépites'."""
    data = build_gem_finder_data()
    return Response(data)
