from datetime import date

from django.test import Client

from catalog.models import Game, Genre
from geography.models import Country, GoogleTrendsInterest


def test_trends_api_empty(client: Client, db: None) -> None:
    response = client.get("/api/stats/trends/")
    assert response.status_code == 200
    assert response.json() == {"timeline": [], "series": {}}


def test_trends_api_with_data_and_filters(client: Client, db: None) -> None:
    game = Game.objects.create(appid=105600, name="Terraria")
    genre = Genre.objects.create(name="Survival")
    game.genres.add(genre)

    country_fr = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    country_us = Country.objects.create(iso2="US", iso3="USA", name_fr="États-Unis")

    d1 = date(2026, 1, 1)
    d2 = date(2026, 2, 1)

    GoogleTrendsInterest.objects.create(game=game, country=country_fr, date=d1, interest=40)
    GoogleTrendsInterest.objects.create(game=game, country=country_us, date=d1, interest=80)
    GoogleTrendsInterest.objects.create(game=game, country=country_fr, date=d2, interest=60)

    # Test sans filtre
    res = client.get("/api/stats/trends/")
    assert res.status_code == 200
    data = res.json()
    assert data["timeline"] == ["2026-01-01", "2026-02-01"]
    assert data["series"]["2026-01-01"]["FRA"] == 40
    assert data["series"]["2026-01-01"]["USA"] == 80
    assert data["series"]["2026-02-01"]["FRA"] == 60

    # Test filtre appid
    res_game = client.get(f"/api/stats/trends/?appid={game.appid}")
    assert res_game.status_code == 200
    assert len(res_game.json()["timeline"]) == 2

    # Test filtre genre
    res_genre = client.get("/api/stats/trends/?genre=Survival")
    assert res_genre.status_code == 200
    assert len(res_genre.json()["timeline"]) == 2
