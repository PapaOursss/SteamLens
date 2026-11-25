from collections import defaultdict
from datetime import timedelta

from django.db.models import Max, Sum
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from players.models import TwitchLanguageDay, TwitchMonth, TwitchTopSnapshot

TOP_GAMES = 20
TOP_LANGUAGES = 12
LANGUAGE_WINDOW_DAYS = 7
RACE_TOP_DEFAULT = 15

SAMPLE_TOP = [
    ("Just Chatting", None, 420_000, 7_800),
    ("Grand Theft Auto V", 271590, 210_000, 4_100),
    ("League of Legends", None, 180_000, 3_200),
    ("Counter-Strike", 730, 120_000, 2_900),
    ("VALORANT", None, 95_000, 2_600),
    ("Dota 2", 570, 60_000, 900),
]
SAMPLE_LANGUAGES = [("en", 52), ("es", 12), ("pt", 7), ("de", 6), ("fr", 5), ("ru", 5), ("ja", 4)]
SAMPLE_RACE = {
    "2016-01": [("League of Legends", 127_000), ("Counter-Strike", 64_000), ("Dota 2", 60_000)],
    "2020-04": [("Just Chatting", 270_000), ("League of Legends", 210_000), ("VALORANT", 180_000)],
    "2024-09": [
        ("Just Chatting", 364_000),
        ("League of Legends", 160_000),
        ("Counter-Strike", 78_000),
    ],
}


def _sample_stats() -> dict:
    return {
        "is_sample": True,
        "taken_at": None,
        "top": [
            {
                "rank": rank,
                "name": name,
                "appid": appid,
                "box_art_url": "",
                "viewers": viewers,
                "streams": streams,
            }
            for rank, (name, appid, viewers, streams) in enumerate(SAMPLE_TOP, start=1)
        ],
        "languages": [{"language": code, "share": share} for code, share in SAMPLE_LANGUAGES],
    }


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def twitch_stats(request: Request) -> Response:
    """Le dernier top Twitch relevé, et la part des langues des streams sur sept jours."""
    latest = TwitchTopSnapshot.objects.aggregate(latest=Max("taken_at"))["latest"]
    if latest is None:
        return Response(_sample_stats())

    snapshots = TwitchTopSnapshot.objects.filter(taken_at=latest).select_related("category")
    top = [
        {
            "rank": snapshot.rank,
            "name": snapshot.category.name,
            "appid": snapshot.category.game_id,
            "box_art_url": snapshot.category.box_art_url,
            "viewers": snapshot.viewer_count,
            "streams": snapshot.stream_count,
        }
        for snapshot in snapshots.order_by("rank")[:TOP_GAMES]
    ]
    return Response(
        {"is_sample": False, "taken_at": latest, "top": top, "languages": _language_shares(latest)}
    )


def _language_shares(latest) -> list[dict]:
    since = latest.date() - timedelta(days=LANGUAGE_WINDOW_DAYS - 1)
    hours = (
        TwitchLanguageDay.objects.filter(day__gte=since)
        .values("language")
        .annotate(hours=Sum("viewer_hours"))
        .order_by("-hours")
    )
    total = sum(row["hours"] for row in hours) or 1
    return [
        {"language": row["language"], "share": round(100 * row["hours"] / total, 1)}
        for row in hours[:TOP_LANGUAGES]
    ]


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="top", type=int, required=False, description="Jeux par mois (défaut : 15)"
        ),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def twitch_history(request: Request) -> Response:
    """Spectateurs moyens du top Twitch mois par mois depuis 2016, pour la course de barres."""
    top = request.query_params.get("top", "")
    limit = int(top) if top.isdecimal() and int(top) > 0 else RACE_TOP_DEFAULT

    timeline: dict[str, list[dict]] = defaultdict(list)
    rows = TwitchMonth.objects.filter(rank__lte=limit).order_by("month", "rank")
    for row in rows.values("month", "name", "game_id", "avg_viewers"):
        timeline[row["month"].strftime("%Y-%m")].append(
            {"appid": row["game_id"], "name": row["name"], "players": row["avg_viewers"]}
        )
    if not timeline:
        timeline = {
            month: [{"appid": None, "name": name, "players": avg} for name, avg in games]
            for month, games in SAMPLE_RACE.items()
        }
        return Response({"is_sample": True, "months": list(timeline), "timeline": timeline})
    return Response({"is_sample": False, "months": sorted(timeline), "timeline": timeline})
