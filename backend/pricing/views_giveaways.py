from datetime import UTC, datetime

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ingestion.http import ApiError
from ingestion.sources.gamerpower import GamerPowerClient


def build_client() -> GamerPowerClient:
    return GamerPowerClient()


@extend_schema(
    responses=inline_serializer(
        "Giveaway",
        {
            "id": serializers.IntegerField(),
            "title": serializers.CharField(),
            "image": serializers.CharField(),
            "url": serializers.CharField(),
            "end_date": serializers.CharField(allow_null=True),
        },
        many=True,
    )
)
@api_view(["GET"])
def giveaways(request: Request) -> Response:
    """Jeux Steam offerts en ce moment ; une offre passée, encore en cache, est retirée (T-48)."""
    try:
        offers = build_client().active_giveaways()
    except ApiError:
        return Response(
            {"detail": "GamerPower ne répond pas."}, status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    return Response([o for o in offers if o["end_date"] is None or o["end_date"] >= now])
