from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewCounts:
    """Total des avis d'un jeu dans une langue (`query_summary` de Steam)."""

    appid: int
    language: str
    positive: int
    negative: int
