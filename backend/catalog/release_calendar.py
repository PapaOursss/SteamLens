from collections import defaultdict
from typing import Any

from django.db.models.functions import ExtractIsoWeekDay, ExtractMonth, ExtractYear

from catalog.models import Game

MONTH_LABELS = [
    "Jan",
    "Fév",
    "Mar",
    "Avr",
    "Mai",
    "Juin",
    "Juil",
    "Août",
    "Sep",
    "Oct",
    "Nov",
    "Déc",
]

DAY_LABELS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]


def _fallback_calendar_stats() -> dict[str, Any]:
    """Données synthétiques réalistes reflétant les dynamiques des sorties Steam."""
    # Matrice jour de la semaine (1=Lundi .. 7=Dimanche) x mois (1..12)
    # Le jeudi (index 3) et le vendredi (index 4) concentrent les sorties
    weekday_month: list[list[int]] = []
    base_counts = [12, 18, 22, 55, 45, 15, 8]  # Lu, Ma, Me, Je, Ve, Sa, Di

    for day_idx in range(7):
        for month_idx in range(12):
            multiplier = 1.0 + (
                0.3 if month_idx in (9, 10, 11) else (-0.2 if month_idx in (6, 7) else 0.0)
            )
            count = int(base_counts[day_idx] * multiplier)
            weekday_month.append([day_idx, month_idx, count])

    # Calendrier quotidien façon GitHub pour l'année courante ou récente
    year = 2026
    daily_contributions: list[list[Any]] = []
    import datetime

    start_date = datetime.date(year, 1, 1)
    end_date = datetime.date(year, 12, 31)
    curr = start_date
    while curr <= end_date:
        weekday = curr.weekday()  # 0=Monday
        month = curr.month
        base = base_counts[weekday] // 4
        if month in (10, 11):
            base += 4
        daily_contributions.append([curr.isoformat(), max(1, base)])
        curr += datetime.timedelta(days=1)

    return {
        "is_sample": True,
        "weekday_month": weekday_month,
        "daily_contributions": daily_contributions,
        "selected_year": year,
        "available_years": [2026, 2025, 2024, 2023],
        "days": DAY_LABELS,
        "months": MONTH_LABELS,
    }


def build_release_calendar_stats(year: int | None = None) -> dict[str, Any]:
    """Construit les statistiques de calendrier des sorties : heatmap jour x mois et quotidien."""
    qs = Game.objects.filter(release_date__isnull=False)
    if not qs.exists():
        return _fallback_calendar_stats()

    # 1. Heatmap globale jour x mois
    # ExtractIsoWeekDay donne 1 (lundi) à 7 (dimanche)
    annotated = qs.annotate(
        weekday=ExtractIsoWeekDay("release_date"),
        month=ExtractMonth("release_date"),
        rel_year=ExtractYear("release_date"),
    ).values("weekday", "month", "rel_year")

    weekday_month_counts: dict[tuple[int, int], int] = defaultdict(int)
    years_found: set[int] = set()
    daily_counts_by_year: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for row in annotated:
        w = row["weekday"] - 1  # 0=Lundi..6=Dimanche
        m = row["month"] - 1  # 0=Jan..11=Dec
        y = row["rel_year"]
        weekday_month_counts[(w, m)] += 1
        if y:
            years_found.add(y)

    available_years = sorted(years_found, reverse=True)
    target_year = (
        year
        if (year and year in available_years)
        else (available_years[0] if available_years else 2026)
    )

    # Récupérer les dates pour l'année ciblée
    for game in qs.filter(release_date__year=target_year):
        d_str = game.release_date.isoformat()
        daily_counts_by_year[target_year][d_str] += 1

    weekday_month_list = [
        [day_idx, month_idx, weekday_month_counts.get((day_idx, month_idx), 0)]
        for day_idx in range(7)
        for month_idx in range(12)
    ]

    daily_list = [
        [d_str, count] for d_str, count in sorted(daily_counts_by_year[target_year].items())
    ]

    return {
        "is_sample": False,
        "weekday_month": weekday_month_list,
        "daily_contributions": daily_list,
        "selected_year": target_year,
        "available_years": available_years or [2026],
        "days": DAY_LABELS,
        "months": MONTH_LABELS,
    }
