import re
import unicodedata
from collections.abc import Iterable

from django.db.models import F

from catalog.models import Game

TRADEMARKS = re.compile(r"[™®©]")
SPACES = re.compile(r"\s+")


def normalize_name(name: str) -> str:
    """« ELDEN RING™ » et « Elden Ring » donnent la même clé."""
    text = unicodedata.normalize("NFKC", TRADEMARKS.sub("", name)).replace("’", "'")
    return SPACES.sub(" ", text).strip().casefold()


def appids_by_name(names: Iterable[str]) -> dict[str, int]:
    """Nom Twitch → appid Steam, par nom identique ; le jeu le plus possédé gagne les homonymes."""
    wanted = {normalize_name(name): name for name in names}
    found: dict[str, int] = {}
    games = Game.objects.order_by(F("owners_mid").desc(nulls_last=True), "appid").values_list(
        "appid", "name"
    )
    for appid, game_name in games.iterator():
        original = wanted.get(normalize_name(game_name))
        if original is not None and original not in found:
            found[original] = appid
    return found


def appids_by_igdb(igdb_ids: Iterable[int]) -> dict[int, int]:
    """id IGDB (donné par Twitch) → appid Steam, grâce au lien posé par l'import IGDB (T-11)."""
    return dict(Game.objects.filter(igdb_id__in=set(igdb_ids)).values_list("igdb_id", "appid"))
