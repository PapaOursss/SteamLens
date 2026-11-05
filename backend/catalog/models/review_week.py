from django.db import models


class ReviewWeek(models.Model):
    """Avis récents d'un jeu sur une semaine : des comptes seulement, jamais d'auteur (T-22)."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="review_weeks")
    week_start = models.DateField()
    positive = models.PositiveIntegerField(default=0)
    negative = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["game", "week_start"], name="unique_review_week"),
        )
        ordering = ("week_start",)

    @property
    def total(self) -> int:
        return self.positive + self.negative

    def __str__(self) -> str:
        return f"{self.game_id} · semaine du {self.week_start}"
