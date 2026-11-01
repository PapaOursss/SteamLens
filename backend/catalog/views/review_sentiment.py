from django.db.models import F, Sum
from django.db.models.functions import ExtractYear
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import ReviewSummary

DEFAULT_LANGUAGE = "english"
SHARE_DECIMALS = 3


@extend_schema(
    parameters=[OpenApiParameter("language", str, description="langue des avis (english)")],
    responses=inline_serializer(
        "ReviewSentiment",
        {
            "genre": serializers.CharField(),
            "year": serializers.IntegerField(),
            "positive": serializers.IntegerField(),
            "negative": serializers.IntegerField(),
            "positive_share": serializers.FloatField(),
        },
        many=True,
    ),
)
@api_view(["GET"])
def review_sentiment(request: Request) -> Response:
    """Part d'avis positifs par genre et par année de sortie (6 M d'avis Kaggle, T-47)."""
    language = request.query_params.get("language", DEFAULT_LANGUAGE)
    rows = (
        ReviewSummary.objects.filter(
            language=language,
            game__release_date__isnull=False,
            game__genres__isnull=False,
        )
        .annotate(genre=F("game__genres__name"), year=ExtractYear("game__release_date"))
        .values("genre", "year")
        .annotate(positive_total=Sum("positive"), negative_total=Sum("negative"))
        .order_by("genre", "year")
    )
    return Response(
        [
            {
                "genre": row["genre"],
                "year": row["year"],
                "positive": row["positive_total"],
                "negative": row["negative_total"],
                "positive_share": round(
                    row["positive_total"] / (row["positive_total"] + row["negative_total"]),
                    SHARE_DECIMALS,
                ),
            }
            for row in rows
            if row["positive_total"] + row["negative_total"]
        ]
    )
