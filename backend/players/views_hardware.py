from django.db.models import Max
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from players.models import HardwareShare

CATEGORIES = ("language", "os", "gpu", "ram", "vr")
DEFAULT_CATEGORY = "language"
DEFAULT_TOP = 8
MAX_TOP = 30
# Courbes mises en avant par le ticket T-27.
HIGHLIGHTS = (
    ("Chinois simplifié", "language", "Simplified Chinese"),
    ("Linux", "os", "Linux"),
    ("Steam Deck (SteamOS Holo)", "os", "SteamOS Holo 64 bit"),
)


def _top_items(category: str, top: int) -> list[str]:
    """Les éléments les plus répandus au dernier mois connu de la catégorie."""
    latest = HardwareShare.objects.filter(category=category).aggregate(month=Max("month"))
    rows = HardwareShare.objects.filter(category=category, month=latest["month"])
    return list(rows.order_by("-percent").values_list("item", flat=True)[:top])


def _series(category: str, items: list[str], months: list) -> list[dict]:
    values = {
        (row.item, row.month): float(row.percent)
        for row in HardwareShare.objects.filter(category=category, item__in=items)
    }
    return [
        {"item": item, "values": [values.get((item, month)) for month in months]} for item in items
    ]


def _top_param(request: Request) -> int:
    raw = request.query_params.get("top", str(DEFAULT_TOP))
    if not raw.isdigit():
        raise ValidationError({"top": "nombre entier attendu"})
    return min(int(raw), MAX_TOP)


@extend_schema(
    parameters=[
        OpenApiParameter("category", str, enum=CATEGORIES, description="catégorie suivie"),
        OpenApiParameter("top", int, description="nombre de courbes (8 par défaut)"),
    ],
    responses=inline_serializer(
        "HardwareSurvey",
        {
            "category": serializers.CharField(),
            "months": serializers.ListField(child=serializers.DateField()),
            "series": serializers.ListField(child=serializers.DictField()),
            "highlights": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def hardware_survey(request: Request) -> Response:
    """Enquête Steam mois par mois : une courbe par élément le plus répandu de la catégorie."""
    category = request.query_params.get("category", DEFAULT_CATEGORY)
    if category not in CATEGORIES:
        raise ValidationError({"category": f"une de : {', '.join(CATEGORIES)}"})
    months = sorted(set(HardwareShare.objects.values_list("month", flat=True)))
    highlights = [
        {"label": label, **_series(highlight_category, [item], months)[0]}
        for label, highlight_category, item in HIGHLIGHTS
    ]
    return Response(
        {
            "category": category,
            "months": months,
            "series": _series(category, _top_items(category, _top_param(request)), months),
            "highlights": highlights,
        }
    )
