from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta

from ingestion.sources.steam_reviews.recent_review import RecentReview


@dataclass
class WeekCounts:
    positive: int = 0
    negative: int = 0


def week_start(day: date) -> date:
    """Le lundi de la semaine du jour donné."""
    return day - timedelta(days=day.weekday())


def count_by_week(reviews: Iterable[RecentReview]) -> dict[date, WeekCounts]:
    """Avis 👍 et 👎 comptés par semaine (lundi), l'auteur est oublié au passage."""
    weeks: dict[date, WeekCounts] = {}
    for review in reviews:
        counts = weeks.setdefault(week_start(review.created_at.date()), WeekCounts())
        if review.voted_up:
            counts.positive += 1
        else:
            counts.negative += 1
    return weeks


def sum_by_week(days: Mapping[date, WeekCounts]) -> dict[date, WeekCounts]:
    """Jours regroupés par semaine ; une première semaine entamée en cours de route est ôtée."""
    weeks: dict[date, WeekCounts] = {}
    for day, counts in days.items():
        week = weeks.setdefault(week_start(day), WeekCounts())
        week.positive += counts.positive
        week.negative += counts.negative
    if days and min(days).weekday() != 0:
        del weeks[week_start(min(days))]
    return {start: week for start, week in weeks.items() if week.positive + week.negative}
