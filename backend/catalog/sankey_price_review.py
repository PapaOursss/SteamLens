from collections import Counter
from typing import Any

from catalog.models import Game
from catalog.priced_games import priced_games

PRICE_BRACKETS = [
    "Gratuit",
    "< 5 €",
    "5-15 €",
    "15-30 €",
    "> 30 €",
]

# Au-delà, les genres rares (logiciels, vidéo…) rejoignent « Autres genres ».
TOP_GENRES = 8
OTHER_GENRES = "Autres genres"

REVIEW_BUCKETS = [
    "Négatif",
    "Mitigé",
    "Positif",
    "Très positif",
]


def _get_price_bracket(price: float, is_free: bool) -> str:
    if is_free or price == 0:
        return "Gratuit"
    if price < 5.0:
        return "< 5 €"
    if price <= 15.0:
        return "5-15 €"
    if price <= 30.0:
        return "15-30 €"
    return "> 30 €"


def _get_review_bucket(positive_pct: int) -> str:
    if positive_pct < 40:
        return "Négatif"
    if positive_pct < 70:
        return "Mitigé"
    if positive_pct < 85:
        return "Positif"
    return "Très positif"


def _fallback_sankey() -> dict[str, Any]:
    """Données de fallback réalistes quand la base est encore vide."""
    genres = ["Action", "Aventure", "Indépendant", "RPG", "Stratégie", "Simulation"]
    flows = [
        ("Action", "Gratuit", 25),
        ("Action", "< 5 €", 18),
        ("Action", "5-15 €", 35),
        ("Action", "15-30 €", 40),
        ("Action", "> 30 €", 30),
        ("Aventure", "< 5 €", 15),
        ("Aventure", "5-15 €", 30),
        ("Aventure", "15-30 €", 25),
        ("Aventure", "> 30 €", 12),
        ("Indépendant", "Gratuit", 10),
        ("Indépendant", "< 5 €", 35),
        ("Indépendant", "5-15 €", 60),
        ("Indépendant", "15-30 €", 20),
        ("RPG", "5-15 €", 20),
        ("RPG", "15-30 €", 35),
        ("RPG", "> 30 €", 35),
        ("Stratégie", "< 5 €", 10),
        ("Stratégie", "5-15 €", 25),
        ("Stratégie", "15-30 €", 30),
        ("Stratégie", "> 30 €", 15),
        ("Simulation", "< 5 €", 8),
        ("Simulation", "5-15 €", 22),
        ("Simulation", "15-30 €", 18),
        ("Simulation", "> 30 €", 14),
        # Tranche de prix -> Accueil
        ("Gratuit", "Négatif", 8),
        ("Gratuit", "Mitigé", 12),
        ("Gratuit", "Positif", 10),
        ("Gratuit", "Très positif", 5),
        ("< 5 €", "Négatif", 10),
        ("< 5 €", "Mitigé", 28),
        ("< 5 €", "Positif", 32),
        ("< 5 €", "Très positif", 26),
        ("5-15 €", "Négatif", 12),
        ("5-15 €", "Mitigé", 35),
        ("5-15 €", "Positif", 80),
        ("5-15 €", "Très positif", 65),
        ("15-30 €", "Négatif", 8),
        ("15-30 €", "Mitigé", 25),
        ("15-30 €", "Positif", 65),
        ("15-30 €", "Très positif", 70),
        ("> 30 €", "Négatif", 4),
        ("> 30 €", "Mitigé", 15),
        ("> 30 €", "Positif", 45),
        ("> 30 €", "Très positif", 42),
    ]

    nodes_set = set(genres) | set(PRICE_BRACKETS) | set(REVIEW_BUCKETS)
    nodes = [{"name": name} for name in nodes_set]
    links = [{"source": src, "target": tgt, "value": val} for src, tgt, val in flows]
    return {
        "is_sample": True,
        "nodes": sorted(nodes, key=lambda n: n["name"]),
        "links": links,
        "genres": sorted(genres),
        "price_brackets": PRICE_BRACKETS,
        "review_buckets": REVIEW_BUCKETS,
    }


def _main_genres(games: list[Game]) -> dict[int, str]:
    """Un genre par jeu, le plus courant des siens : chaque jeu passe une fois par colonne."""
    frequency = Counter(genre.name for game in games for genre in game.genres.all())
    kept = {name for name, _ in frequency.most_common(TOP_GENRES)}
    main: dict[int, str] = {}
    for game in games:
        names = sorted((genre.name for genre in game.genres.all()), key=lambda n: -frequency[n])
        if names:
            main[game.appid] = names[0] if names[0] in kept else OTHER_GENRES
    return main


def build_sankey_data() -> dict[str, Any]:
    """Construit les flux Sankey : genre principal -> tranche de prix -> accueil (avis)."""
    measured = priced_games().prefetch_related("genres")
    games = [game for game in measured if game.positive + game.negative]
    main_genres = _main_genres(games)
    if not main_genres:
        return _fallback_sankey()

    genre_to_price: Counter[tuple[str, str]] = Counter()
    price_to_review: Counter[tuple[str, str]] = Counter()
    for game in games:
        genre = main_genres.get(game.appid)
        if genre is None:
            continue
        price = float(game.latest_price) if game.latest_price is not None else 0.0
        bracket = _get_price_bracket(price, game.is_free)
        positive_percent = int(game.positive * 100 / (game.positive + game.negative))
        genre_to_price[genre, bracket] += 1
        price_to_review[bracket, _get_review_bucket(positive_percent)] += 1

    genres = sorted(set(main_genres.values()))
    links = [
        {"source": source, "target": target, "value": count}
        for flows in (genre_to_price, price_to_review)
        for (source, target), count in flows.items()
    ]
    return {
        "is_sample": False,
        "nodes": [{"name": name} for name in sorted({*genres, *PRICE_BRACKETS, *REVIEW_BUCKETS})],
        "links": links,
        "genres": genres,
        "price_brackets": PRICE_BRACKETS,
        "review_buckets": REVIEW_BUCKETS,
    }
