"""Repérer les « review bombings » : une semaine où le ratio d'avis positifs s'effondre (T-22)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

from catalog.models import ReviewWeek

MIN_WEEK_REVIEWS = 20
BASELINE_WEEKS = 4
# Chute du ratio positif, en points de pourcentage, par rapport aux semaines d'avant.
BOMBING_DROP = 0.20
SHARE_DECIMALS = 3


@dataclass(frozen=True)
class Bombing:
    week_start: date
    positive_share: float
    baseline_share: float
    drop: float
    reviews: int


def positive_share(week: ReviewWeek) -> float:
    return week.positive / week.total if week.total else 0.0


def find_bombings(weeks: Sequence[ReviewWeek]) -> list[Bombing]:
    """Semaines dont le ratio positif tombe d'au moins `BOMBING_DROP` sous la moyenne des
    `BASELINE_WEEKS` semaines précédentes ; les semaines trop creuses sont ignorées."""
    solid_weeks = [week for week in sorted(weeks, key=lambda w: w.week_start)
                   if week.total >= MIN_WEEK_REVIEWS]  # fmt: skip
    bombings = []
    for index in range(BASELINE_WEEKS, len(solid_weeks)):
        before = solid_weeks[index - BASELINE_WEEKS : index]
        baseline = sum(positive_share(week) for week in before) / BASELINE_WEEKS
        week = solid_weeks[index]
        drop = baseline - positive_share(week)
        if drop >= BOMBING_DROP:
            bombings.append(
                Bombing(
                    week_start=week.week_start,
                    positive_share=round(positive_share(week), SHARE_DECIMALS),
                    baseline_share=round(baseline, SHARE_DECIMALS),
                    drop=round(drop, SHARE_DECIMALS),
                    reviews=week.total,
                )
            )
    return bombings
