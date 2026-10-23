from django.db import models


class PlayerCountSnapshot(models.Model):
    """Nombre de joueurs connectés à un jeu à un instant : on fabrique l'historique."""

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="player_counts"
    )
    taken_at = models.DateTimeField(db_index=True)
    players = models.PositiveIntegerField()
    source = models.CharField(max_length=32)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "taken_at", "source"], name="unique_player_count_snapshot"
            ),
        )
        ordering = ("taken_at",)

    def __str__(self) -> str:
        return f"{self.game_id} · {self.players} · {self.taken_at:%Y-%m-%d %H:%M}"
