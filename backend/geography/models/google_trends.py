from django.db import models


class GoogleTrendsInterest(models.Model):
    """Score d'intérêt relatif Google Trends (0-100) par jeu, région et date."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="trends_interest")
    country = models.ForeignKey("geography.Country", on_delete=models.CASCADE, related_name="trends_interest")
    date = models.DateField(db_index=True)
    interest = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("-date", "-interest")
        unique_together = ("game", "country", "date")

    def __str__(self) -> str:
        return f"{self.game.name} · {self.country.iso3} · {self.date} : {self.interest}"
