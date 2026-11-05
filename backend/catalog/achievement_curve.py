"""Courbe d'abandon et taux de fin d'un jeu à partir de ses succès (T-35)."""

import re
from collections.abc import Sequence
from itertools import pairwise
from statistics import median

from catalog.models import AchievementStat

# Mots qui trahissent un succès de fin d'histoire, dans son nom ou sa description.
ENDING_KEYWORDS = (
    "ending", "finish the game", "finish the story", "complete the game",
    "complete the story", "complete the campaign", "beat the game", "credits",
    "final boss", "the end", "fin du jeu", "terminer le jeu", "terminer l'histoire",
)  # fmt: skip
ENDING_PATTERN = re.compile(rf"\b(?:{'|'.join(map(re.escape, ENDING_KEYWORDS))})\b")
PERCENT_DECIMALS = 2


def is_ending(achievement: AchievementStat) -> bool:
    # Les noms d'API (`ACH_TRUE_ENDING`) séparent les mots par des tirets bas.
    raw = f"{achievement.name} {achievement.display_name} {achievement.description}"
    text = raw.lower().replace("_", " ")
    return ENDING_PATTERN.search(text) is not None


def completion_rate(achievements: Sequence[AchievementStat]) -> float | None:
    """Part des joueurs qui ont vu la fin : le plus courant des succès de fin repérés."""
    endings = [float(achievement.percent) for achievement in achievements if is_ending(achievement)]
    return max(endings) if endings else None


def abandon_curve(achievements: Sequence[AchievementStat]) -> list[dict]:
    """Succès du plus courant au plus rare : la pente montre où les joueurs lâchent."""
    ordered = sorted(achievements, key=lambda achievement: achievement.percent, reverse=True)
    return [
        {
            "rank": rank,
            "name": achievement.display_name or achievement.name,
            "percent": float(achievement.percent),
            "is_ending": is_ending(achievement),
        }
        for rank, achievement in enumerate(ordered, start=1)
    ]


def biggest_drop(curve: Sequence[dict]) -> dict | None:
    """Le plus grand écart entre deux succès voisins de la courbe."""
    steps = [
        {
            "from_achievement": before["name"],
            "to_achievement": after["name"],
            "drop": before["percent"] - after["percent"],
        }
        for before, after in pairwise(curve)
    ]
    if not steps:
        return None
    step = max(steps, key=lambda row: row["drop"])
    return {**step, "drop": round(step["drop"], PERCENT_DECIMALS)}


def median_percent(achievements: Sequence[AchievementStat]) -> float:
    return round(median(float(a.percent) for a in achievements), PERCENT_DECIMALS)
