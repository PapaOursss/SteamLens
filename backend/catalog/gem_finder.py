from typing import Any

from django.db.models import F, Q
from django.db.models.functions import ExtractYear

from catalog.models import Game
from catalog.priced_games import priced_games

MAX_SCATTER_GAMES = 2000
MAX_GEMS = 600
MIN_REVIEWS = 50
PERCENT = 100
PRICE_COUNTRIES = ("FR", "US")
GEM_MAX_PRICE = 15.0
GEM_MIN_SCORE = 85
GEM_MAX_OWNERS = 500_000


def _build_game_item(
    game: Game, price: float, score: int, owners: int, year: int | None
) -> dict[str, Any]:
    is_gem = (price <= GEM_MAX_PRICE) and (score >= GEM_MIN_SCORE) and (owners <= GEM_MAX_OWNERS)
    genres = list(game.genres.all())
    genre_name = genres[0].name if genres else "Autre"
    return {
        "appid": game.appid,
        "name": game.name,
        "header_image": game.header_image or "",
        "price_eur": round(price, 2),
        "positive_percent": score,
        "owners": owners,
        "genre": genre_name,
        "year": year,
        "is_gem": is_gem,
    }


def _scatter_games() -> list[Game]:
    """Les pépites d'abord, sinon le tri par possesseurs écarterait les jeux méconnus.

    Prix français, sinon le prix américain converti (dataset Kaggle) : le prix français n'est
    relevé que pour quelques centaines de jeux. Moins de `MIN_REVIEWS` avis : la note ne dit
    rien. Possesseurs inconnus : le jeu est laissé de côté, jamais inventé.
    """
    judged = (
        priced_games(PRICE_COUNTRIES)
        .annotate(
            year=ExtractYear("release_date"),
            review_count=F("positive") + F("negative"),
            positive_hundredths=F("positive") * PERCENT,
        )
        .filter(owners_mid__isnull=False, review_count__gte=MIN_REVIEWS)
        .prefetch_related("genres")
        .order_by("-owners_mid", "appid")
    )
    # Même règle que `_build_game_item`, en entiers pour éviter les arrondis de SQLite.
    is_gem = Q(
        latest_price__lte=GEM_MAX_PRICE,
        owners_mid__lte=GEM_MAX_OWNERS,
        positive_hundredths__gte=F("review_count") * GEM_MIN_SCORE,
    )
    gems = list(judged.filter(is_gem)[:MAX_GEMS])
    others = list(
        judged.exclude(appid__in=[game.appid for game in gems])[: MAX_SCATTER_GAMES - len(gems)]
    )
    return gems + others


def build_gem_finder_data() -> dict[str, Any]:
    """Points du nuage « chercheur de pépites » : toutes les pépites, puis les plus possédés."""
    items: list[dict[str, Any]] = []
    genres_set: set[str] = set()
    years_set: set[int] = set()

    for game in _scatter_games():
        total_reviews = game.positive + game.negative
        price_val = float(game.latest_price) if game.latest_price is not None else 0.0
        score = int((game.positive / total_reviews) * 100)

        item = _build_game_item(game, price_val, score, game.owners_mid, game.year)
        items.append(item)
        genres_set.add(item["genre"])
        if item["year"]:
            years_set.add(item["year"])

    is_sample = not items
    if is_sample:
        # Données de démonstration si la base est vide
        items = _fallback_gems()
        for it in items:
            genres_set.add(it["genre"])
            if it["year"]:
                years_set.add(it["year"])

    return {
        "is_sample": is_sample,
        "games": items,
        "genres": sorted(genres_set),
        "years": sorted(years_set),
        "gem_criteria": {
            "max_price": GEM_MAX_PRICE,
            "min_score": GEM_MIN_SCORE,
            "max_owners": GEM_MAX_OWNERS,
        },
    }


def _fallback_gems() -> list[dict[str, Any]]:
    return [
        {
            "appid": 413150,
            "name": "Stardew Valley",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/413150/header.jpg",
            "price_eur": 13.99,
            "positive_percent": 98,
            "owners": 350000,
            "genre": "Simulation",
            "year": 2016,
            "is_gem": True,
        },
        {
            "appid": 730,
            "name": "Counter-Strike 2",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg",
            "price_eur": 0.0,
            "positive_percent": 88,
            "owners": 50000000,
            "genre": "Action",
            "year": 2012,
            "is_gem": False,
        },
        {
            "appid": 264710,
            "name": "Subnautica",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/264710/header.jpg",
            "price_eur": 29.99,
            "positive_percent": 96,
            "owners": 4000000,
            "genre": "Aventure",
            "year": 2018,
            "is_gem": False,
        },
        {
            "appid": 367520,
            "name": "Hollow Knight",
            "header_image": "https://cdn.akamai.steamstatic.com/steam/apps/367520/header.jpg",
            "price_eur": 14.79,
            "positive_percent": 97,
            "owners": 450000,
            "genre": "Action",
            "year": 2017,
            "is_gem": True,
        },
    ]
