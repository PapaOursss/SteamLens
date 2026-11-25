from django.db import models


class TwitchTopSnapshot(models.Model):
    """Place d'une catégorie dans le top Twitch à une heure donnée, avec ses spectateurs."""

    category = models.ForeignKey(
        "players.TwitchCategory", on_delete=models.CASCADE, related_name="snapshots"
    )
    taken_at = models.DateTimeField(db_index=True)
    rank = models.PositiveSmallIntegerField()
    viewer_count = models.PositiveIntegerField(default=0)
    stream_count = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["category", "taken_at"], name="unique_twitch_top_snapshot"
            ),
        )
        ordering = ("-taken_at", "rank")

    def __str__(self) -> str:
        return f"{self.taken_at:%Y-%m-%d %H:%M} · n°{self.rank} {self.category_id}"
