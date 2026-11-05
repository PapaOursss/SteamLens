from django.db import models


class IgdbPopularity(models.Model):
    """Un indicateur du PopScore IGDB (visites, envies, joueurs…) : un second avis sur la
    popularité d'un jeu, à côté des chiffres Steam."""

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="igdb_popularity"
    )
    popularity_type = models.CharField(max_length=64)
    value = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "popularity_type"], name="unique_igdb_popularity"
            ),
        )
        ordering = ("game", "popularity_type")

    def __str__(self) -> str:
        return f"{self.game_id} · {self.popularity_type} = {self.value}"
