from django.db.models import Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from geography.models import RegionalSales


def _mock_regional_genre_sales() -> list[dict]:
    return [
        {"genre": "Action", "na": 877.8, "eu": 525.0, "jp": 159.9, "other": 187.4},
        {"genre": "Sports", "na": 683.3, "eu": 376.5, "jp": 135.4, "other": 135.0},
        {"genre": "Shooter", "na": 582.6, "eu": 313.2, "jp": 38.3, "other": 102.7},
        {"genre": "Role-Playing", "na": 319.5, "eu": 183.6, "jp": 344.9, "other": 59.6},
        {"genre": "Platform", "na": 447.0, "eu": 201.6, "jp": 130.8, "other": 51.6},
        {"genre": "Misc", "na": 402.5, "eu": 213.8, "jp": 107.8, "other": 74.4},
        {"genre": "Racing", "na": 359.4, "eu": 238.4, "jp": 56.7, "other": 77.3},
    ]


def _favorite(by_genre: list[dict], region: str) -> str:
    return max(by_genre, key=lambda row: row[region])["genre"]


@extend_schema(
    responses=inline_serializer(
        "RegionalSalesBreakdown",
        {
            "by_genre": serializers.ListField(child=serializers.DictField()),
            "top_regions": serializers.DictField(),
            "is_sample": serializers.BooleanField(),
        },
    ),
)
@api_view(["GET"])
def regional_sales_stats(request: Request) -> Response:
    """Ventes par genre en Amérique du Nord, en Europe, au Japon et dans le reste du monde.

    Tant que `import_kaggle_vgsales` n'a pas tourné, des chiffres d'exemple (`is_sample`).
    """
    qs = (
        RegionalSales.objects.values("genre")
        .annotate(
            na=Sum("na_sales"),
            eu=Sum("eu_sales"),
            jp=Sum("jp_sales"),
            other=Sum("other_sales"),
        )
        .order_by("-na")
    )
    by_genre = [
        {
            "genre": item["genre"],
            "na": round(item["na"] or 0.0, 1),
            "eu": round(item["eu"] or 0.0, 1),
            "jp": round(item["jp"] or 0.0, 1),
            "other": round(item["other"] or 0.0, 1),
        }
        for item in qs
    ]
    is_sample = not by_genre
    if is_sample:
        by_genre = _mock_regional_genre_sales()

    favorites = {region: _favorite(by_genre, region) for region in ("na", "eu", "jp")}
    top_regions = {
        "na_favorite": favorites["na"],
        "eu_favorite": favorites["eu"],
        "jp_favorite": favorites["jp"],
        "notes": (
            f"Genre en tête : {favorites['na']} en Amérique du Nord, {favorites['eu']} en Europe, "
            f"{favorites['jp']} au Japon."
        ),
    }

    return Response({"by_genre": by_genre, "top_regions": top_regions, "is_sample": is_sample})
