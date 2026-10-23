from django.db import models


class GameTag(models.Model):
    """Lien jeu ↔ tag, avec le nombre de joueurs qui ont voté ce tag."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="game_tags")
    tag = models.ForeignKey("catalog.Tag", on_delete=models.CASCADE, related_name="game_tags")
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["game", "tag"], name="unique_game_tag"),
        )
        ordering = ("-votes",)

    def __str__(self) -> str:
        return f"{self.game_id} · {self.tag} ({self.votes})"
