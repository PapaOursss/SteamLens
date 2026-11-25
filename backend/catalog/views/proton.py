from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Genre, ProtonReport

MAX_GENRES = 15
COUNTED_TIERS = ("platinum", "gold", "silver", "bronze", "borked")


def _tiers_by_genre() -> list[dict]:
    genres = list(Genre.objects.all()[:MAX_GENRES])
    counts = {genre.id: dict.fromkeys(COUNTED_TIERS, 0) for genre in genres}
    rows = (
        ProtonReport.objects.filter(game__genres__in=list(counts), tier__in=COUNTED_TIERS)
        .order_by()
        .values_list("game__genres", "tier")
        .annotate(total=Count("id"))
    )
    for genre_id, tier, total in rows:
        counts[genre_id][tier] = total
    return [{"genre": genre.name, "counts": counts[genre.id]} for genre in genres]


@extend_schema(
    responses=inline_serializer(
        "ProtonStats",
        {
            "tiers": serializers.ListField(child=serializers.DictField()),
            "by_genre": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def proton_stats(request: Request) -> Response:
    """Statistiques globales et répartition par genre des niveaux de compatibilité Proton."""
    tier_counts = ProtonReport.objects.values("tier").annotate(total=Count("id")).order_by("-total")

    genre_breakdown = _tiers_by_genre()

    return Response(
        {
            "tiers": list(tier_counts),
            "by_genre": genre_breakdown,
        }
    )
