from collections import Counter, defaultdict

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from catalog.models import Game

# Sous ce nombre de jeux, le genre « de prédilection » d'un pays ne veut rien dire.
MIN_GAMES_FOR_GENRE = 5
# Un genre doit compter quelques jeux dans le pays pour être retenu.
MIN_GENRE_GAMES = 2
TOP_GENRES = 5

SAMPLE = [
    ("USA", "États-Unis", 120, 410, "Simulation", 1.2),
    ("JPN", "Japon", 35, 140, "RPG", 2.1),
    ("GBR", "Royaume-Uni", 30, 95, "Course", 1.9),
    ("FRA", "France", 22, 60, "Aventure", 1.4),
    ("POL", "Pologne", 14, 40, "Simulation", 2.3),
    ("SWE", "Suède", 12, 38, "Stratégie", 1.8),
]


def _sample() -> dict:
    return {
        "is_sample": True,
        "countries": [
            {
                "iso3": iso3,
                "name": name,
                "studios": studios,
                "games": games,
                "favorite_genre": genre,
                "favorite_index": index,
                "top_genres": [{"genre": genre, "games": games // 3, "index": index}],
                "top_studios": [],
            }
            for iso3, name, studios, games, genre, index in SAMPLE
        ],
    }


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
def studio_countries(request: Request) -> Response:
    """Studios et jeux par pays d'origine du studio, et le genre que chaque pays fait le plus.

    « Genre de prédilection » = le plus surreprésenté par rapport aux jeux de tous les pays
    (indice de spécificité), pas le plus fréquent : sinon ce serait « Indé » partout.
    """
    links = (
        Game.developers.through.objects.filter(company__country__isnull=False)
        .values_list("game_id", "company_id", "company__name", "company__country__iso3",
                     "company__country__name_fr")
    )  # fmt: skip
    games_by_country: dict[str, set[int]] = defaultdict(set)
    studios_by_country: dict[str, Counter[str]] = defaultdict(Counter)
    names: dict[str, str] = {}
    for appid, _, studio, iso3, name in links:
        games_by_country[iso3].add(appid)
        studios_by_country[iso3][studio] += 1
        names[iso3] = name
    if not games_by_country:
        return Response(_sample())

    all_games = set().union(*games_by_country.values())
    genres_by_game: dict[int, list[str]] = defaultdict(list)
    genre_links = Game.genres.through.objects.filter(game_id__in=all_games)
    for appid, genre in genre_links.values_list("game_id", "genre__name"):
        genres_by_game[appid].append(genre)
    world = Counter(genre for genres in genres_by_game.values() for genre in genres)

    countries = []
    for iso3, games in games_by_country.items():
        top_genres = _specific_genres(games, genres_by_game, world, len(all_games))
        favorite = top_genres[0] if len(games) >= MIN_GAMES_FOR_GENRE and top_genres else None
        countries.append(
            {
                "iso3": iso3,
                "name": names[iso3],
                "studios": len(studios_by_country[iso3]),
                "games": len(games),
                "favorite_genre": favorite["genre"] if favorite else None,
                "favorite_index": favorite["index"] if favorite else None,
                "top_genres": top_genres,
                "top_studios": [
                    {"name": studio, "games": count}
                    for studio, count in studios_by_country[iso3].most_common(TOP_GENRES)
                ],
            }
        )
    countries.sort(key=lambda row: (-row["games"], row["name"]))
    return Response({"is_sample": False, "countries": countries})


def _specific_genres(
    games: set[int], genres_by_game: dict[int, list[str]], world: Counter[str], world_games: int
) -> list[dict]:
    local = Counter(genre for appid in games for genre in genres_by_game.get(appid, []))
    scored = [
        {
            "genre": genre,
            "games": count,
            "index": round((count / len(games)) / (world[genre] / world_games), 2),
        }
        for genre, count in local.items()
        if count >= MIN_GENRE_GAMES
    ]
    return sorted(scored, key=lambda row: (-row["index"], -row["games"]))[:TOP_GENRES]
