from django.db import models


class ReviewSummary(models.Model):
    """Avis d'un jeu dans une langue à une date : des comptes, jamais d'auteur."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="reviews")
    language = models.CharField(max_length=32)
    positive = models.PositiveIntegerField(default=0)
    negative = models.PositiveIntegerField(default=0)
    date = models.DateField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "language", "date"], name="unique_review_summary"
            ),
        )
        ordering = ("-date",)

    @property
    def total(self) -> int:
        return self.positive + self.negative

    def __str__(self) -> str:
        return f"{self.game_id} · {self.language} · {self.date}"
