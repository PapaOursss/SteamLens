import json
from collections.abc import Callable
from typing import Any

from django.conf import settings

from catalog.models import Game
from config.stats_cache import database_version
from ingestion.models import ImportRun

# À changer quand le calcul d'une statistique change : les fichiers d'avant sont refaits.
FORMAT_VERSION = 1
# Relevés horaires : ils ne touchent ni aux jeux, ni aux genres, ni aux tags.
HOURLY_SOURCES = ("snapshot_players", "snapshot_twitch", "twitch")


def data_version() -> str:
    """Change après chaque import du catalogue, ou quand la base est remplacée."""
    last_import = (
        ImportRun.objects.filter(finished_at__isnull=False)
        .exclude(source__in=HOURLY_SOURCES)
        .order_by("-finished_at")
        .values_list("finished_at", flat=True)
        .first()
    )
    return f"{FORMAT_VERSION}|{last_import}|{Game.objects.count()}"


def precomputed(name: str, build: Callable[[], Any]) -> Any:
    """Résultat gardé sur disque tant que le catalogue n'a pas changé, sinon recalculé."""
    if database_version() is None:
        return build()
    path = settings.PRECOMPUTED_DIR / f"{name}.json"
    version = data_version()
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry["version"] == version:
            return entry["data"]
    except (OSError, ValueError, KeyError):
        pass
    data = build()
    path.parent.mkdir(parents=True, exist_ok=True)
    # Écrit à côté puis renommé : le site et le planificateur partagent ces fichiers.
    partial = path.with_suffix(f".{id(data)}.tmp")
    partial.write_text(json.dumps({"version": version, "data": data}), encoding="utf-8")
    partial.replace(path)
    return data
