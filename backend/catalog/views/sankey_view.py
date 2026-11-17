from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.sankey_price_review import build_sankey_data


@extend_schema(
    responses=inline_serializer(
        "SankeyPriceReviewResponse",
        {
            "nodes": inline_serializer("SankeyNode", {"name": serializers.CharField()}, many=True),
            "links": inline_serializer(
                "SankeyLink",
                {
                    "source": serializers.CharField(),
                    "target": serializers.CharField(),
                    "value": serializers.IntegerField(),
                },
                many=True,
            ),
            "genres": serializers.ListField(child=serializers.CharField()),
            "price_brackets": serializers.ListField(child=serializers.CharField()),
            "review_buckets": serializers.ListField(child=serializers.CharField()),
        },
    )
)
@api_view(["GET"])
def sankey_price_review_stats(request: Request) -> Response:
    """Diagramme Sankey : Genre -> Tranche de prix -> Accueil des avis."""
    data = build_sankey_data()
    return Response(data)
