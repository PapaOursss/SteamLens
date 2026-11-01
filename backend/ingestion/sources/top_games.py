from catalog.models import Game


def most_owned_appids(limit: int) -> list[int]:
    """Les jeux les plus possédés d'après SteamSpy (T-08) : la liste que suivent les imports."""
    return list(
        Game.objects.filter(owners_mid__isnull=False)
        .order_by("-owners_mid", "-peak_ccu", "appid")
        .values_list("appid", flat=True)[:limit]
    )
