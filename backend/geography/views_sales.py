from django.db.models import Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from geography.models import RegionalSales


def _mock_regional_genre_sales() -> list[dict]:
    return [
        {"genre": "Action", "na": 877.8, "eu": 525.0, "jp": 159.9},
        {"genre": "Sports", "na": 683.3, "eu": 376.5, "jp": 135.4},
        {"genre": "Shooter", "na": 582.6, "eu": 313.2, "jp": 38.3},
        {"genre": "Role-Playing", "na": 319.5, "eu": 183.6, "jp": 344.9},
        {"genre": "Platform", "na": 447.0, "eu": 201.6, "jp": 130.8},
        {"genre": "Misc", "na": 402.5, "eu": 213.8, "jp": 107.8},
        {"genre": "Racing", "na": 359.4, "eu": 238.4, "jp": 56.7},
    ]


@extend_schema(
    responses=inline_serializer(
        "RegionalSalesBreakdown",
        {
            "by_genre": serializers.ListField(child=serializers.DictField()),
            "top_regions": serializers.DictField(),
        },
    ),
)
@api_view(["GET"])
def regional_sales_stats(request: Request) -> Response:
    """Répartition des ventes de jeux par genre et par région (Amérique du Nord, Europe, Japon)."""
    qs = (
        RegionalSales.objects.values("genre")
        .annotate(
            na=Sum("na_sales"),
            eu=Sum("eu_sales"),
            jp=Sum("jp_sales"),
        )
        .order_by("-na")
    )
    if not qs.exists():
        by_genre = _mock_regional_genre_sales()
    else:
        by_genre = [
            {
                "genre": item["genre"],
                "na": round(item["na"] or 0.0, 1),
                "eu": round(item["eu"] or 0.0, 1),
                "jp": round(item["jp"] or 0.0, 1),
            }
            for item in qs
        ]

    top_regions = {
        "na_favorite": "Action",
        "eu_favorite": "Action",
        "jp_favorite": "Role-Playing",
        "notes": "Les joueurs japonais plébiscitent massivement le RPG par rapport au reste du monde.",
    }

    return Response({
        "by_genre": by_genre,
        "top_regions": top_regions,
    })
