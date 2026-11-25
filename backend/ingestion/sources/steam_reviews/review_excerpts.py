from collections.abc import Iterable

from ingestion.sources.steam_reviews.recent_review import RecentReview

# Les deux langues des nuages de mots (T-40), noms de l'API Steam.
EXCERPT_LANGUAGES = ("english", "french")
EXCERPTS_PER_SIDE = 50
MAX_EXCERPT_LENGTH = 2000


def pick_excerpts(reviews: Iterable[RecentReview]) -> list[RecentReview]:
    """Les premiers avis non vides de chaque langue et de chaque sens, texte raccourci.

    Le SteamID est vidé : l'extrait ne garde que le texte, le sens et la langue.
    """
    counts: dict[tuple[str, bool], int] = {}
    picked: list[RecentReview] = []
    for review in reviews:
        key = (review.language, review.voted_up)
        text = review.text.strip()
        if review.language not in EXCERPT_LANGUAGES or not text:
            continue
        if counts.get(key, 0) >= EXCERPTS_PER_SIDE:
            continue
        counts[key] = counts.get(key, 0) + 1
        picked.append(
            RecentReview(
                created_at=review.created_at,
                voted_up=review.voted_up,
                author_steamid="",
                language=review.language,
                text=text[:MAX_EXCERPT_LENGTH],
            )
        )
    return picked
