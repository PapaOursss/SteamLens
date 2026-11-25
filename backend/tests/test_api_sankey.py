import pytest
from django.test import Client

from catalog.models import Game, Genre, ReviewSummary
from geography.models import Country
from pricing.models import PricePoint


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_sankey_price_review_with_games(client: Client) -> None:
    genre_rpg = Genre.objects.create(name="RPG")
    g1 = Game.objects.create(appid=2001, name="Cheap Good RPG", is_free=False)
    g1.genres.add(genre_rpg)
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    PricePoint.objects.create(
        game=g1, country=france, currency="EUR", price="4.99", price_eur="4.99", date="2026-01-01"
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


def add_reviews(game: Game, positive: int, negative: int) -> None:
    ReviewSummary.objects.create(
        game=game, language="all", positive=positive, negative=negative, date="2026-01-01"
    )


@pytest.mark.django_db
def test_sankey_counts_each_game_once_in_every_column(client: Client) -> None:
    action = Genre.objects.create(name="Action")
    rpg = Genre.objects.create(name="RPG")
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    game = Game.objects.create(appid=2002, name="Action RPG")
    game.genres.add(action, rpg)
    PricePoint.objects.create(
        game=game, country=france, currency="EUR", price="9.99", price_eur="9.99", date="2026-01-01"
    )
    add_reviews(game, positive=80, negative=20)

    links = client.get("/api/stats/sankey-pricing/").json()["links"]

    from_genres = sum(link["value"] for link in links if link["target"] == "5-15 €")
    to_reviews = sum(link["value"] for link in links if link["source"] == "5-15 €")
    assert from_genres == to_reviews == 1


@pytest.mark.django_db
def test_sankey_leaves_out_free_games_whose_store_page_was_never_read(client: Client) -> None:
    action = Genre.objects.create(name="Action")
    read = Game.objects.create(
        appid=2003, name="Read", is_free=True, store_fetched_at="2026-01-01T00:00:00Z"
    )
    unread = Game.objects.create(appid=2004, name="Unread", is_free=True)
    for game in (read, unread):
        game.genres.add(action)
        add_reviews(game, positive=50, negative=50)

    links = client.get("/api/stats/sankey-pricing/").json()["links"]

    free_games = sum(link["value"] for link in links if link["target"] == "Gratuit")
    assert free_games == 1
