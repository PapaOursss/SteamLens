from django.db.models import F, Max, Sum
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from geography.models import ProfileCountryCount, ProfileSample

SHARE_DECIMALS = 3
TOP_COUNTRIES = 20


def _share(part: int, whole: int) -> float:
    return round(part / whole, SHARE_DECIMALS) if whole else 0.0


def _sample(day: object) -> dict:
    totals = ProfileSample.objects.filter(date=day).aggregate(
        profiles=Sum("profiles"), without=Sum("without_country"), unmapped=Sum("unmapped_country")
    )
    profiles = totals["profiles"] or 0
    return {
        "date": day,
        "games": ProfileSample.objects.filter(date=day).count(),
        "profiles": profiles,
        "without_country": totals["without"] or 0,
        "without_country_share": _share(totals["without"] or 0, profiles),
        "unmapped_country": totals["unmapped"] or 0,
    }


def _countries(day: object) -> list[dict]:
    rows = list(
        ProfileCountryCount.objects.filter(date=day)
        .values(iso3=F("country__iso3"), name=F("country__name_fr"))
        .annotate(profiles=Sum("profiles"))
        .order_by("-profiles")
    )
    located = sum(row["profiles"] for row in rows)
    return [{**row, "share": _share(row["profiles"], located)} for row in rows[:TOP_COUNTRIES]]


def _by_genre(day: object) -> list[dict]:
    """Pays le plus représenté de chaque genre, avec sa part des profils localisés du genre."""
    rows = (
        ProfileCountryCount.objects.filter(date=day, game__genres__isnull=False)
        .values(genre=F("game__genres__name"), name=F("country__name_fr"))
        .annotate(profiles=Sum("profiles"))
    )
    genres: dict[str, dict] = {}
    for row in rows:
        entry = genres.setdefault(row["genre"], {"genre": row["genre"], "located": 0, "top": row})
        entry["located"] += row["profiles"]
        if row["profiles"] > entry["top"]["profiles"]:
            entry["top"] = row
    return sorted(
        (
            {
                "genre": entry["genre"],
                "profiles": entry["located"],
                "top_country": entry["top"]["name"],
                "top_country_share": _share(entry["top"]["profiles"], entry["located"]),
            }
            for entry in genres.values()
        ),
        key=lambda row: row["profiles"],
        reverse=True,
    )


@extend_schema(
    responses=inline_serializer(
        "ProfileCountries",
        {
            "sample": serializers.DictField(),
            "countries": serializers.ListField(child=serializers.DictField()),
            "by_genre": serializers.ListField(child=serializers.DictField()),
        },
    ),
)
@api_view(["GET"])
def profile_countries(request: Request) -> Response:
    """Carte n°6 : pays déclarés des profils publics, avec la taille de l'échantillon."""
    day = ProfileSample.objects.aggregate(day=Max("date"))["day"]
    return Response(
        {"sample": _sample(day), "countries": _countries(day), "by_genre": _by_genre(day)}
    )
