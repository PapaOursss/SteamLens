from collections.abc import Iterable
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
