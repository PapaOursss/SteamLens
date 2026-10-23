from django.test import Client

FRONT_ORIGIN = "http://localhost:3000"


def test_health_answers_ok(client: Client) -> None:
    response = client.get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_allows_the_nuxt_front(client: Client) -> None:
    response = client.get("/api/health/", HTTP_ORIGIN=FRONT_ORIGIN)

    assert response.headers["Access-Control-Allow-Origin"] == FRONT_ORIGIN
