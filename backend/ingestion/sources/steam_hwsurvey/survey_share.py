from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SurveyShare:
    """Une ligne de l'enquête : part des joueurs pour un élément d'une catégorie."""

    month: date
    category: str
    item: str
    percent: float
