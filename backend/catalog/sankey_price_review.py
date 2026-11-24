from collections import defaultdict
from typing import Any

from django.db.models import OuterRef, Q, Subquery

from catalog.models import Game, ReviewSummary
from pricing.models import PricePoint

PRICE_BRACKETS = [
    "Gratuit",
    "< 5 €",
    "5-15 €",
    "15-30 €",
    "> 30 €",
]

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
        "nodes": sorted(nodes, key=lambda n: n["name"]),
        "links": links,
        "genres": sorted(genres),
        "price_brackets": PRICE_BRACKETS,
        "review_buckets": REVIEW_BUCKETS,
    }


def build_sankey_data() -> dict[str, Any]:
    """Construit les flux Sankey: Genre -> Tranche de prix -> Accueil (avis)."""
    latest_price_subquery = (
        PricePoint.objects.filter(game=OuterRef("pk"), country="FR", price_eur__isnull=False)
        .order_by("-date")
        .values("price_eur")[:1]
    )

    latest_review = ReviewSummary.objects.filter(game=OuterRef("pk"), language="all").order_by(
        "-date"
    )

    # Prix ou avis inconnus : le jeu est laissé de côté, jamais inventé.
    games = list(
        Game.objects.annotate(
            latest_price=Subquery(latest_price_subquery),
            positive=Subquery(latest_review.values("positive")[:1]),
            negative=Subquery(latest_review.values("negative")[:1]),
        )
        .filter(
            Q(latest_price__isnull=False) | Q(is_free=True),
            genres__isnull=False,
            positive__isnull=False,
        )
        .prefetch_related("genres")
        .distinct()[:500]
    )

    if not games:
        return _fallback_sankey()

    genre_to_price: dict[tuple[str, str], int] = defaultdict(int)
    price_to_review: dict[tuple[str, str], int] = defaultdict(int)
    active_genres: set[str] = set()

    for game in games:
        total_rev = game.positive + game.negative
        if not total_rev:
            continue
        price_val = float(game.latest_price) if game.latest_price is not None else 0.0
        price_bracket = _get_price_bracket(price_val, game.is_free)

        positive_pct = int((game.positive / total_rev) * 100)
        review_bucket = _get_review_bucket(positive_pct)

        for genre in game.genres.all()[:2]:
            genre_to_price[(genre.name, price_bracket)] += 1
            price_to_review[(price_bracket, review_bucket)] += 1
            active_genres.add(genre.name)

    nodes_set = active_genres | set(PRICE_BRACKETS) | set(REVIEW_BUCKETS)
    nodes = [{"name": name} for name in sorted(nodes_set)]

    links: list[dict[str, Any]] = []
    for (genre, bracket), count in genre_to_price.items():
        links.append({"source": genre, "target": bracket, "value": count})
    for (bracket, review_b), count in price_to_review.items():
        links.append({"source": bracket, "target": review_b, "value": count})

    return {
        "nodes": nodes,
        "links": links,
        "genres": sorted(active_genres),
        "price_brackets": PRICE_BRACKETS,
        "review_buckets": REVIEW_BUCKETS,
    }
