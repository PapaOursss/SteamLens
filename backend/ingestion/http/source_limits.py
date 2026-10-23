"""Écart minimal entre deux appels, par source, pour rester sous les limites des API gratuites."""

SECONDS_PER_MINUTE = 60

MIN_INTERVAL_SECONDS: dict[str, float] = {
    # ~200 requêtes par 5 minutes.
    "steam_store": 5 * SECONDS_PER_MINUTE / 200,
    # 100 000 appels par jour : une seconde suffit largement.
    "steam_web_api": 1.0,
    # 1 requête par seconde, sauf `request=all` : 1 par minute.
    "steamspy": 1.0,
    "steamspy_all": SECONDS_PER_MINUTE,
    # 4 requêtes par seconde.
    "igdb": 1 / 4,
    # 800 points par minute.
    "twitch": SECONDS_PER_MINUTE / 800,
    # 20 000 requêtes par mois : on espace un peu pour ne pas tout brûler d'un coup.
    "rawg": 0.5,
}

DEFAULT_MIN_INTERVAL_SECONDS = 1.0


def min_interval_for(source: str) -> float:
    return MIN_INTERVAL_SECONDS.get(source, DEFAULT_MIN_INTERVAL_SECONDS)
