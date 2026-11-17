from django.test import Client

from catalog.models import Game, Genre, ReviewSummary
from pricing.models import PricePoint


def test_sankey_price_review_empty_fallback(client: Client) -> None:
    response = client.get("/api/stats/sankey-pricing/")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) > 0
    assert len(data["links"]) > 0
    assert "price_brackets" in data
    assert "review_buckets" in data


def test_sankey_price_review_with_games(client: Client) -> None:
    genre_rpg = Genre.objects.create(name="RPG")
    g1 = Game.objects.create(appid=2001, name="Cheap Good RPG", is_free=False)
    g1.genres.add(genre_rpg)
    PricePoint.objects.create(
        game=g1, country="FR", currency="EUR", price="4.99", price_eur="4.99", date="2026-01-01"
    )
    ReviewSummary.objects.create(
        game=g1, language="all", positive=90, negative=10, date="2026-01-01"
    )

    response = client.get("/api/stats/sankey-pricing/")
    assert response.status_code == 200
    data = response.json()

    node_names = {n["name"] for n in data["nodes"]}
    assert "RPG" in node_names
    assert "< 5 €" in node_names
    assert "Très positif" in node_names

    # Check links
    links = data["links"]
    link_genre_price = next(
        (l for l in links if l["source"] == "RPG" and l["target"] == "< 5 €"), None
    )
    assert link_genre_price is not None
    assert link_genre_price["value"] >= 1

    link_price_review = next(
        (l for l in links if l["source"] == "< 5 €" and l["target"] == "Très positif"), None
    )
    assert link_price_review is not None
    assert link_price_review["value"] >= 1
