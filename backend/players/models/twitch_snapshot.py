from django.db import models


class TwitchStreamSnapshot(models.Model):
    """Nombre de spectateurs et streams Twitch pour un jeu à un instant."""

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="twitch_snapshots"
    )
    taken_at = models.DateTimeField(db_index=True)
    viewer_count = models.PositiveIntegerField(default=0)
    stream_count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "taken_at"], name="unique_twitch_snapshot"
            ),
        )
        ordering = ("-taken_at",)

    def __str__(self) -> str:
        return f"{self.game.name} · {self.viewer_count} spectateurs · {self.taken_at:%Y-%m-%d %H:%M}"
