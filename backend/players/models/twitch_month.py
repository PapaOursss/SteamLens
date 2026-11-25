from django.db import models


class TwitchMonth(models.Model):
    """Un jeu du top 200 mensuel de Twitch depuis 2016 (dataset Kaggle, relevés SullyGnome)."""

    name = models.CharField(max_length=255)
    month = models.DateField(db_index=True)
    rank = models.PositiveSmallIntegerField()
    hours_watched = models.PositiveBigIntegerField(default=0)
    avg_viewers = models.PositiveIntegerField(default=0)
    peak_viewers = models.PositiveIntegerField(default=0)
    streamers = models.PositiveIntegerField(default=0)
    game = models.ForeignKey(
        "catalog.Game",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="twitch_months",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["name", "month"], name="unique_twitch_month"),
        )
        ordering = ("-month", "rank")

    def __str__(self) -> str:
        return f"{self.month:%Y-%m} · n°{self.rank} {self.name}"
