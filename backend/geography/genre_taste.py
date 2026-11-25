"""Genres surreprésentés par pays, approchés par la langue des avis (T-23).

Steam ne dit pas d'où vient un joueur. On mesure donc les genres des jeux commentés dans une
langue, on les reporte sur les pays qui la parlent, puis on compare à la moyenne mondiale :
indice 1 = comme partout, 2 = deux fois plus. Les volumes d'avis d'une langue se partagent
entre ses pays selon leur population.
"""

from collections import defaultdict

from catalog.models import Game, ReviewSummary
from geography.country_table import BY_ISO2
from geography.language_table import COUNTRY_LANGUAGES
from geography.models import CountryIndicator

TOP_GENRES = 10
# Un genre presque absent du monde donne des indices énormes qui ne veulent rien dire.
MIN_WORLD_SHARE = 0.01
DECIMALS = 3

type Totals = dict[str, float]


def _language_names() -> set[str]:
    return {language for languages in COUNTRY_LANGUAGES.values() for language in languages}


def _reviews_by_game() -> dict[tuple[int, str], int]:
    """Dernier total d'avis de chaque jeu dans chaque langue suivie."""
    rows = (
        ReviewSummary.objects.filter(language__in=_language_names())
        .order_by("date")
        .values_list("game_id", "language", "positive", "negative")
    )
    return {(game, language): up + down for game, language, up, down in rows}


def _genres_by_game(game_ids: set[int]) -> dict[int, list[str]]:
    genres: dict[int, list[str]] = defaultdict(list)
    links = Game.genres.through.objects.filter(game_id__in=game_ids)
    for game_id, name in links.values_list("game_id", "genre__name"):
        genres[game_id].append(name)
    return genres


def genre_shares_by_language() -> tuple[dict[str, Totals], Totals]:
    """Part de chaque genre par langue, et avis par langue ; un jeu à n genres compte 1/n."""
    reviews = _reviews_by_game()
    genres = _genres_by_game({game for game, _ in reviews})
    counts: dict[str, Totals] = defaultdict(lambda: defaultdict(float))
    totals: Totals = defaultdict(float)
    for (game, language), total in reviews.items():
        names = genres.get(game, [])
        if not names or not total:
            continue
        totals[language] += total
        for name in names:
            counts[language][name] += total / len(names)
    shares = {
        language: {name: count / totals[language] for name, count in by_genre.items()}
        for language, by_genre in counts.items()
    }
    return shares, totals


def _speakers() -> dict[str, Totals]:
    """Habitants de chaque pays rattachés à chaque langue ; sans population, chacun vaut 1."""
    populations = dict(
        CountryIndicator.objects.filter(indicator=CountryIndicator.POPULATION).values_list(
            "country_id", "value"
        )
    )
    return {
        iso2: {name: populations.get(iso2, 1.0) * part for name, part in languages.items()}
        for iso2, languages in COUNTRY_LANGUAGES.items()
    }


def _estimated_reviews(totals: Totals) -> dict[str, Totals]:
    """Avis de chaque langue partagés entre ses pays, au prorata des habitants."""
    speakers = _speakers()
    by_language: Totals = defaultdict(float)
    for languages in speakers.values():
        for name, count in languages.items():
            by_language[name] += count
    return {
        iso2: {
            name: totals[name] * count / by_language[name]
            for name, count in languages.items()
            if totals.get(name)
        }
        for iso2, languages in speakers.items()
    }


def _mix(shares: dict[str, Totals], weights: Totals) -> Totals:
    whole = sum(weights.values())
    mixed: Totals = defaultdict(float)
    for language, weight in weights.items():
        for genre, share in shares[language].items():
            mixed[genre] += share * weight / whole
    return mixed


def _country(iso2: str, local: Totals, world: Totals, weights: Totals) -> dict:
    ranked = sorted(
        (
            {
                "genre": genre,
                "share": round(local.get(genre, 0.0), DECIMALS),
                "index": round(local.get(genre, 0.0) / share, DECIMALS),
            }
            for genre, share in world.items()
            if share >= MIN_WORLD_SHARE
        ),
        key=lambda row: (-row["index"], row["genre"]),
    )[:TOP_GENRES]
    return {
        "iso3": BY_ISO2[iso2].iso3,
        "name": BY_ISO2[iso2].name_fr,
        "dominant": ranked[0]["genre"],
        "reviews": round(sum(weights.values())),
        "languages": sorted(weights),
        "genres": ranked,
    }


def genres_by_country() -> dict:
    shares, totals = genre_shares_by_language()
    if not totals:
        return {"genres": [], "countries": []}
    world = _mix(shares, totals)
    countries = [
        _country(iso2, _mix(shares, weights), world, weights)
        for iso2, weights in _estimated_reviews(totals).items()
        if weights
    ]
    countries.sort(key=lambda row: row["name"])
    return {"genres": sorted({row["dominant"] for row in countries}), "countries": countries}
