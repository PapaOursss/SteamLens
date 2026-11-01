from django.test import Client

from catalog.models import Game


def test_studios_map_is_keyed_by_iso3(client: Client, catalog_sample: dict[str, Game]) -> None:
    assert client.get("/api/map/studios/").json() == {"FRA": 1, "USA": 1}


def test_average_price_map_is_in_euros(client: Client, catalog_sample: dict[str, Game]) -> None:
    assert client.get("/api/map/average-price-eur/").json() == {"FRA": 13.99, "USA": 12.8}


def test_unknown_indicator_lists_the_known_ones(
    client: Client, catalog_sample: dict[str, Game]
) -> None:
    response = client.get("/api/map/nope/")

    assert response.status_code == 404
    assert "average-price-eur, studios" in response.json()["detail"]


def test_api_docs_page_is_served(client: Client, db: None) -> None:
    assert client.get("/api/schema/").status_code == 200
    assert client.get("/api/docs/").status_code == 200
