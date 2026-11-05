from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameRecord:
    """Un jeu tel qu'une source le décrit, prêt à écrire par `GameWriter`.

    `fields` porte les colonnes de `Game` à remplir (vides et None ignorés) ; le reste, ce
    sont les liens et les chiffres rangés dans d'autres tables.
    """

    appid: int
    name: str = ""
    fields: dict[str, Any] = field(default_factory=dict)
    genres: list[str] = field(default_factory=list)
    tag_votes: dict[str, int] = field(default_factory=dict)
    developers: list[str] = field(default_factory=list)
    publishers: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    average_playtime_minutes: int | None = None
    median_playtime_minutes: int | None = None
    positive_reviews: int | None = None
    negative_reviews: int | None = None
