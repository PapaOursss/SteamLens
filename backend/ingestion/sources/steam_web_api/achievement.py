from dataclasses import dataclass


@dataclass(frozen=True)
class Achievement:
    """Un succès et la part des joueurs qui l'ont débloqué, en pourcentage."""

    name: str
    percent: float
    display_name: str = ""
    description: str = ""
