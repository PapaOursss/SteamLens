from django.db import models


class RankingEntry(models.Model):
    """Place d'un jeu dans un classement SteamSpy (top 100 sur deux semaines, de tous les temps)."""

    TOP_100_IN_2_WEEKS = "top100in2weeks"
    TOP_100_FOREVER = "top100forever"
    CHART_CHOICES = (
        (TOP_100_IN_2_WEEKS, "Top 100 des deux dernières semaines"),
        (TOP_100_FOREVER, "Top 100 de tous les temps"),
    )

    chart = models.CharField(max_length=32, choices=CHART_CHOICES)
    date = models.DateField()
    rank = models.PositiveSmallIntegerField()
    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="rankings")

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["chart", "date", "rank"], name="unique_ranking_entry"),
        )
        ordering = ("chart", "-date", "rank")

    def __str__(self) -> str:
        return f"{self.chart} · {self.date} · n°{self.rank} {self.game_id}"
