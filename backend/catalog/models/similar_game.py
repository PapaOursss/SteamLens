from django.db import models


class SimilarGame(models.Model):
    """Un des 10 jeux les plus proches d'un autre par ses tags (cosinus, T-41), précalculé."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="similar_links")
    similar = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="+")
    rank = models.PositiveSmallIntegerField()
    score = models.FloatField()

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["game", "rank"], name="unique_similar_game_rank"),
        )
        ordering = ("game", "rank")

    def __str__(self) -> str:
        return f"{self.game_id} → {self.similar_id} ({self.score:.2f})"
