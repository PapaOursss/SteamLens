"""« ADN du jeu » (T-14) : six axes, chacun rangé de 0 à 100 parmi les jeux suivis."""

from django.db.models import (
    Avg,
    Case,
    Expression,
    F,
    FloatField,
    OuterRef,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Cast, NullIf

from catalog.models import AchievementStat, Game, ReviewSummary
from ingestion.writing.game_writer import ALL_LANGUAGES
from players.models import TwitchStreamSnapshot
from pricing.models import PricePoint

PERCENT = 100.0
FRANCE_ISO2 = "FR"
ROUNDING_DIGITS = 2


def _latest(rows: QuerySet, field: str, order: str) -> Subquery:
    """Valeur du dernier relevé d'un jeu, en nombre décimal."""
    latest_rows = rows.filter(game=OuterRef("pk")).order_by(f"-{order}")
    return Subquery(latest_rows.values(field)[:1], output_field=FloatField())


def _rating() -> Expression:
    shares = ReviewSummary.objects.filter(language=ALL_LANGUAGES).annotate(
        share=F("positive") * PERCENT / NullIf(F("positive") + F("negative"), 0)
    )
    return _latest(shares, "share", "date")


def _france_price() -> Expression:
    prices = PricePoint.objects.filter(country_id=FRANCE_ISO2)
    return Case(
        When(is_free=True, then=Value(0.0)),
        default=_latest(prices, "price_eur", "date"),
        output_field=FloatField(),
    )


def _achievement_rarity() -> Expression:
    """Part moyenne des joueurs qui débloquent un succès, retournée : 100 = succès très rares."""
    averages = (
        AchievementStat.objects.filter(game=OuterRef("pk"))
        .values("game")
        .annotate(average=Avg("percent"))
        .values("average")
    )
    return PERCENT - Cast(Subquery(averages[:1]), FloatField())


def axis_metrics() -> dict[str, Expression]:
    """La mesure brute de chaque axe ; un jeu sans donnée sur un axe y vaut None."""
    return {
        "rating": _rating(),
        "popularity": Cast(F("owners_mid"), FloatField()),
        "price": _france_price(),
        "lifespan": Cast(NullIf(F("playtime__median_playtime_minutes"), 0), FloatField()),
        "twitch": _latest(TwitchStreamSnapshot.objects.all(), "viewer_count", "taken_at"),
        "achievement_rarity": _achievement_rarity(),
    }


def percentile(below: int, total: int) -> int:
    """Rang centile : 0 pour le plus bas des jeux mesurés, 100 pour le plus haut."""
    if total <= 1:
        return int(PERCENT)
    return round(below * PERCENT / (total - 1))


def axis_score(game: Game, metric: Expression) -> dict:
    measured = Game.objects.annotate(metric=metric).exclude(metric=None)
    raw = measured.filter(pk=game.pk).values_list("metric", flat=True).first()
    if raw is None:
        return {"score": None, "raw": None}
    below = measured.filter(metric__lt=raw).count()
    return {"score": percentile(below, measured.count()), "raw": round(raw, ROUNDING_DIGITS)}


def game_dna(game: Game) -> list[dict]:
    return [{"key": key, **axis_score(game, metric)} for key, metric in axis_metrics().items()]
