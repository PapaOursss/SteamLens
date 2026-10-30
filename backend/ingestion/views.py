from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from ingestion.models import ImportRun

KNOWN_SOURCES = [
    {
        "key": "kaggle_complete",
        "name": "Kaggle — Steam Games Complete (trolukovich)",
        "logo": "kaggle",
        "role": "Catalogue initial, genres, tags, prix de base, dates de sortie.",
        "license": "CC0: Public Domain",
        "limits": "Données statiques issues d'un snapshot.",
    },
    {
        "key": "kaggle_fronkon",
        "name": "Kaggle — Steam Games Dataset (fronkongames)",
        "logo": "kaggle",
        "role": "Données récentes (~100k jeux), pic de joueurs, langues supportées.",
        "license": "CC0: Public Domain",
        "limits": "Périodicité de mise à jour dépendante des dépôts Kaggle.",
    },
    {
        "key": "steamspy",
        "name": "SteamSpy API",
        "logo": "steamspy",
        "role": "Propriétaires estimés, tags pondérés, classements top 100.",
        "license": "Données publiques SteamSpy",
        "limits": "Fourchettes estimées basées sur des sondages d'inventaires Steam.",
    },
    {
        "key": "steam_web_api",
        "name": "Steam Web API (officielle)",
        "logo": "steam",
        "role": "Comptage des joueurs en direct (CCU) et succès.",
        "license": "Valve Steam API Terms of Use",
        "limits": "Pas d'historique fourni directement, reconstitué par snapshots réguliers.",
    },
    {
        "key": "steam_store",
        "name": "Steam Store API",
        "logo": "steam",
        "role": "Fiches détaillées, captures, prix multidevises par pays.",
        "license": "Valve Steam Store Terms",
        "limits": "API non documentée, débit limité.",
    },
    {
        "key": "igdb",
        "name": "IGDB (Twitch)",
        "logo": "igdb",
        "role": "Taxonomie avancée : genres, thèmes, modes de jeu, PopScore.",
        "license": "Conditions d'utilisation IGDB / Twitch Developer",
        "limits": "Nécessite une authentification OAuth Twitch.",
    },
    {
        "key": "twitch",
        "name": "Twitch Helix API",
        "logo": "twitch",
        "role": "Streams actifs, nombre de spectateurs par jeu et langues de diffusion.",
        "license": "Twitch Developer Services Agreement",
        "limits": "Données très volatiles capturées en direct.",
    },
    {
        "key": "isthereanydeal",
        "name": "IsThereAnyDeal",
        "logo": "itad",
        "role": "Historique des prix, prix le plus bas jamais atteint, soldes.",
        "license": "ITAD API Terms",
        "limits": "Couvre principalement les boutiques partenaires.",
    },
    {
        "key": "cheapshark",
        "name": "CheapShark API",
        "logo": "cheapshark",
        "role": "Promotions actuelles et comparatif multimagasins.",
        "license": "CheapShark Free API",
        "limits": "Dépendant de l'indexation par CheapShark.",
    },
    {
        "key": "frankfurter",
        "name": "Frankfurter API (BCE)",
        "logo": "frankfurter",
        "role": "Taux de change de la Banque Centrale Européenne pour conversion en EUR.",
        "license": "Open Data BCE",
        "limits": "Taux mis à jour quotidiennement (jours ouvrés).",
    },
    {
        "key": "restcountries",
        "name": "REST Countries & Natural Earth",
        "logo": "earth",
        "role": "Métadonnées des pays (codes ISO, devises) et contours cartographiques GeoJSON.",
        "license": "Domaine public / Open Data",
        "limits": "Frontières géopolitiques standardisées 110m.",
    },
    {
        "key": "protondb",
        "name": "ProtonDB API",
        "logo": "protondb",
        "role": "Notes de compatibilité Linux et Steam Deck (Platinum, Gold, etc.).",
        "license": "Données communautaires ProtonDB",
        "limits": "Rapports communautaires avec subjectivité possible.",
    },
]


def _build_source_item(source: dict, latest_runs: dict) -> dict:
    run = latest_runs.get(source["key"])
    return {
        "key": source["key"],
        "name": source["name"],
        "logo": source["logo"],
        "role": source["role"],
        "license": source["license"],
        "limits": source["limits"],
        "last_import": {
            "started_at": run.started_at if run else None,
            "finished_at": run.finished_at if run else None,
            "rows": run.rows if run else 0,
            "succeeded": run.succeeded if run else None,
        },
    }


def _fetch_latest_runs() -> dict:
    runs = {}
    for run in ImportRun.objects.order_by("-started_at"):
        if run.source not in runs:
            runs[run.source] = run
    return runs


@extend_schema(
    responses=inline_serializer(
        "SourcesOverview",
        {
            "pipeline": serializers.DictField(),
            "sources": serializers.ListField(child=serializers.DictField()),
            "methodology_notes": serializers.ListField(child=serializers.CharField()),
        },
    ),
)
@api_view(["GET"])
def sources_overview(request: Request) -> Response:
    """Présentation des sources de données, de leur fraîcheur et de la méthodologie."""
    latest_runs = _fetch_latest_runs()
    sources_data = [_build_source_item(s, latest_runs) for s in KNOWN_SOURCES]

    pipeline = {
        "steps": [
            {
                "step": 1,
                "name": "Collecte",
                "description": "Imports dédiés avec client HTTP partagé (gestion cache et rate limits).",
            },
            {
                "step": 2,
                "name": "Normalisation",
                "description": "Stockage relationnel unifié (Game, Pricing, Players, Geography).",
            },
            {
                "step": 3,
                "name": "Agrégation & API",
                "description": "Endpoints Django REST Framework servant des séries agrégées.",
            },
            {
                "step": 4,
                "name": "Restitution",
                "description": "Application Nuxt 4 avec visualisations ECharts et cartes choroplèthes.",
            },
        ],
    }

    notes = [
        "Aucune donnée personnelle n'est stockée : ni SteamID individuel, ni identifiants.",
        "Les volumes de joueurs par pays sont approximés par les langues ou des sondages agrégés.",
        "Les estimations de propriétaires (SteamSpy) sont présentées par fourchettes.",
    ]

    return Response({
        "pipeline": pipeline,
        "sources": sources_data,
        "methodology_notes": notes,
    })
