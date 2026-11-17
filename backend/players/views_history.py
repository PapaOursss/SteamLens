from collections import defaultdict

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from players.models import PlayerCountSnapshot

TOP_N_DEFAULT = 15


def _mock_timeline() -> dict:
    """Données de secours réalistes si la base n'a pas encore été peuplée."""
    months = ["2018-01", "2019-01", "2020-01", "2021-01", "2022-01", "2023-01", "2024-01"]
    games_sample = [
        {"appid": 730, "name": "Counter-Strike 2", "base": 600000, "grow": 80000},
        {"appid": 570, "name": "Dota 2", "base": 550000, "grow": 10000},
        {"appid": 578080, "name": "PUBG: BATTLEGROUNDS", "base": 1200000, "grow": -100000},
        {"appid": 271590, "name": "Grand Theft Auto V", "base": 120000, "grow": 25000},
        {"appid": 252490, "name": "Rust", "base": 50000, "grow": 18000},
        {"appid": 413150, "name": "Stardew Valley", "base": 30000, "grow": 10000},
        {"appid": 105600, "name": "Terraria", "base": 40000, "grow": 12000},
        {"appid": 1086940, "name": "Baldur's Gate 3", "base": 0, "grow": 80000},
        {"appid": 1245620, "name": "ELDEN RING", "base": 0, "grow": 95000},
        {"appid": 230410, "name": "Warframe", "base": 65000, "grow": 4000},
    ]

    timeline_data = {}
    for idx, month in enumerate(months):
        entries = []
        for g in games_sample:
            p = max(5000, g["base"] + g["grow"] * idx)
            entries.append({"appid": g["appid"], "name": g["name"], "players": p})
        entries.sort(key=lambda x: x["players"], reverse=True)
        timeline_data[month] = entries[:TOP_N_DEFAULT]

    return {
        "months": months,
        "timeline": timeline_data,
    }


@extend_schema(
    parameters=[
        OpenApiParameter(name="top", type=int, required=False, description="Nombre de jeux par mois (défaut : 15)"),
    ],
    responses=OpenApiTypes.OBJECT,
)
@api_view(["GET"])
def monthly_player_race(request: Request) -> Response:
    """Historique mensuel des jeux les plus joués pour bar chart race et bump chart."""
    top_limit = int(request.query_params.get("top", TOP_N_DEFAULT))
    snapshots = (
        PlayerCountSnapshot.objects.select_related("game")
        .order_by("taken_at")
    )

    if not snapshots.exists():
        return Response(_mock_timeline())

    by_month: dict[str, dict[int, dict]] = defaultdict(dict)
    for snap in snapshots:
        m = snap.taken_at.strftime("%Y-%m")
        aid = snap.game_id
        current = by_month[m].get(aid)
        if not current or snap.players > current["players"]:
            by_month[m][aid] = {
                "appid": aid,
                "name": snap.game.name,
                "players": snap.players,
            }

    sorted_months = sorted(by_month.keys())
    if len(sorted_months) < 2:
        return Response(_mock_timeline())

    timeline: dict[str, list[dict]] = {}
    for m in sorted_months:
        ranked = sorted(by_month[m].values(), key=lambda x: x["players"], reverse=True)[:top_limit]
        timeline[m] = ranked

    return Response({
        "months": sorted_months,
        "timeline": timeline,
    })
