from ingestion.sources.steamspy.steamspy_game import SteamSpyGame
from ingestion.writing import GameRecord

LIST_SEPARATOR = ","


def steamspy_record(game: SteamSpyGame) -> GameRecord:
    """Traduit un jeu SteamSpy en ligne à écrire ; `ccu` est le pic de joueurs de la veille."""
    is_free = None if game.initial_price_usd is None else game.initial_price_usd == 0
    return GameRecord(
        appid=game.appid,
        name=game.name,
        fields={
            "owners_min": game.owners.minimum,
            "owners_max": game.owners.maximum,
            "owners_mid": game.owners.midpoint,
            "peak_ccu": game.concurrent_users,
            "supported_languages": game.languages,
            "is_free": is_free,
        },
        genres=game.genres,
        tag_votes=game.tag_votes,
        developers=_split(game.developer),
        publishers=_split(game.publisher),
        average_playtime_minutes=game.average_playtime_minutes or None,
        median_playtime_minutes=game.median_playtime_minutes or None,
        positive_reviews=game.positive_reviews,
        negative_reviews=game.negative_reviews,
    )


def _split(text: str) -> list[str]:
    return [item.strip() for item in text.split(LIST_SEPARATOR) if item.strip()]
