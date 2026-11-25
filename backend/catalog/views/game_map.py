from collections import Counter

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import GameMapPoint

# Familles colorées sur la carte ; les autres jeux sont groupés sous OTHER_FAMILY.
FAMILY_COUNT = 8
OTHER_FAMILY = "Autres"
COORDINATE_DECIMALS = 2


@extend_schema(
    responses=inline_serializer(
        "GameMap",
        {
            "families": serializers.ListField(child=serializers.CharField()),
            "points": inline_serializer(
                "GameMapPoint",
                {
                    "appid": serializers.IntegerField(),
                    "name": serializers.CharField(),
                    "x": serializers.FloatField(),
                    "y": serializers.FloatField(),
                    "family": serializers.CharField(),
                    "owners": serializers.IntegerField(allow_null=True),
                },
                many=True,
            ),
        },
    )
)
@api_view(["GET"])
def game_map(request: Request) -> Response:
    """Carte 2D du catalogue : t-SNE des tags pondérés, couleur = tag principal (T-41)."""
    rows = list(
        GameMapPoint.objects.order_by("game_id").values_list(
            "game_id", "game__name", "x", "y", "main_tag__name", "game__owners_mid"
        )
    )
    counts = Counter(row[4] for row in rows if row[4])
    families = [name for name, _ in counts.most_common(FAMILY_COUNT)]
    points = [
        {
            "appid": appid,
            "name": name,
            "x": round(x, COORDINATE_DECIMALS),
            "y": round(y, COORDINATE_DECIMALS),
            "family": tag if tag in families else OTHER_FAMILY,
            "owners": owners,
        }
        for appid, name, x, y, tag, owners in rows
    ]
    has_others = any(point["family"] == OTHER_FAMILY for point in points)
    return Response({"families": [*families, *([OTHER_FAMILY] if has_others else [])],
                     "points": points})  # fmt: skip
