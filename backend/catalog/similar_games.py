from collections import defaultdict

from catalog.models import Game, GameTag

SHARED_TAGS_SHOWN = 3


def _tag_names_by_game(appids: list[int]) -> dict[int, list[str]]:
    """Tags de chaque jeu, du plus voté au moins voté."""
    names: dict[int, list[str]] = defaultdict(list)
    rows = GameTag.objects.filter(game_id__in=appids).order_by("game_id", "-votes", "tag__name")
    for game_id, tag_name in rows.values_list("game_id", "tag__name"):
        names[game_id].append(tag_name)
    return names


def similar_games(game: Game) -> list[dict]:
    """Les voisins précalculés du jeu, avec les tags qu'ils partagent avec lui."""
    links = list(game.similar_links.select_related("similar").order_by("rank"))
    tags = _tag_names_by_game([game.appid, *(link.similar_id for link in links)])
    own_tags = tags[game.appid]
    return [
        {
            "appid": link.similar.appid,
            "name": link.similar.name,
            "header_image": link.similar.header_image,
            "score": link.score,
            "shared_tags": [name for name in own_tags if name in set(tags[link.similar_id])][
                :SHARED_TAGS_SHOWN
            ],
        }
        for link in links
    ]
