import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from catalog.models import Game, GameMapPoint, GameTag, SimilarGame, Tag
from catalog.similarity import build_tag_matrix, nearest_neighbours
from catalog.views.game_map import OTHER_FAMILY

FARMING = ("Farming Sim", "Cozy", "Pixel Graphics", "Relaxing")
SHOOTER = ("FPS", "Shooter", "Multiplayer", "Competitive")
STARDEW_APPID = 413150


def tag_game(appid: int, name: str, tags: tuple[str, ...], owners: int = 1000) -> Game:
    game = Game.objects.create(appid=appid, name=name, owners_mid=owners)
    for votes, tag_name in enumerate(reversed(tags), start=1):
        tag, _ = Tag.objects.get_or_create(name=tag_name)
        GameTag.objects.create(game=game, tag=tag, votes=votes * 100)
    return game


@pytest.fixture
def catalog(db: None) -> None:
    tag_game(STARDEW_APPID, "Stardew Valley", FARMING, owners=35_000_000)
    tag_game(1, "Coral Island", FARMING[:3] + ("Open World",))
    tag_game(2, "Story of Seasons", FARMING)
    tag_game(730, "Counter-Strike 2", SHOOTER, owners=50_000_000)
    tag_game(3, "Valorant-like", SHOOTER)
    tag_game(4, "Two tags only", ("FPS", "Cozy"))


@pytest.mark.usefixtures("catalog")
def test_games_with_too_few_tags_are_left_out() -> None:
    assert 4 not in build_tag_matrix().appids


@pytest.mark.usefixtures("catalog")
def test_closest_games_share_their_tags() -> None:
    neighbours = nearest_neighbours(build_tag_matrix(), count=2)
    assert [appid for appid, _ in neighbours[STARDEW_APPID]] == [2, 1]
    assert neighbours[STARDEW_APPID][0][1] == 1.0
    assert neighbours[730][0][0] == 3


@pytest.mark.usefixtures("catalog")
def test_command_stores_neighbours_and_map() -> None:
    call_command("compute_similar_games", map_size=4)
    assert SimilarGame.objects.filter(game_id=STARDEW_APPID).count() == 4
    assert SimilarGame.objects.get(game_id=STARDEW_APPID, rank=1).similar_id == 2
    placed = set(GameMapPoint.objects.values_list("game_id", flat=True))
    assert placed == {730, STARDEW_APPID, 1, 2}
    assert GameMapPoint.objects.get(game_id=730).main_tag.name == "FPS"


@pytest.mark.usefixtures("catalog")
def test_command_replaces_previous_results() -> None:
    call_command("compute_similar_games")
    call_command("compute_similar_games")
    assert SimilarGame.objects.filter(game_id=STARDEW_APPID).count() == 4


@pytest.mark.usefixtures("catalog")
def test_api_lists_neighbours_with_shared_tags() -> None:
    call_command("compute_similar_games")
    response = APIClient().get(f"/api/games/{STARDEW_APPID}/similar/")
    first = response.json()[0]
    assert (first["appid"], first["name"], first["score"]) == (2, "Story of Seasons", 1.0)
    assert first["shared_tags"] == ["Farming Sim", "Cozy", "Pixel Graphics"]


@pytest.mark.usefixtures("catalog")
def test_api_map_colours_points_by_main_tag() -> None:
    call_command("compute_similar_games")
    data = APIClient().get("/api/stats/game-map/").json()
    assert set(data["families"]) == {"Farming Sim", "FPS"}
    assert len(data["points"]) == 5
    assert OTHER_FAMILY not in data["families"]


@pytest.mark.django_db
def test_empty_catalogue_is_reported_not_crashed() -> None:
    call_command("compute_similar_games")
    assert not SimilarGame.objects.exists()
    assert APIClient().get("/api/stats/game-map/").json() == {"families": [], "points": []}
