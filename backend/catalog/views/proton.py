from django.db.models import Count
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Genre, ProtonReport


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
    tier_counts = (
        ProtonReport.objects.values("tier")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    genres = Genre.objects.prefetch_related("games__proton_report")[:15]
    genre_breakdown = []
    for genre in genres:
        t_counts = {"platinum": 0, "gold": 0, "silver": 0, "bronze": 0, "borked": 0}
        for game in genre.games.all():
            if hasattr(game, "proton_report") and game.proton_report:
                t = game.proton_report.tier
                if t in t_counts:
                    t_counts[t] += 1
        genre_breakdown.append({
            "genre": genre.name,
            "counts": t_counts,
        })

    return Response({
        "tiers": list(tier_counts),
        "by_genre": genre_breakdown,
    })
