from django.db import models


class GamePlaytime(models.Model):
    """Temps de jeu moyen et médian en minutes (Kaggle / SteamSpy)."""

    game = models.OneToOneField(
        "catalog.Game", on_delete=models.CASCADE, related_name="playtime"
    )
    median_playtime_minutes = models.PositiveIntegerField(default=0)
    average_playtime_minutes = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-median_playtime_minutes",)

    @property
    def median_hours(self) -> float:
        return round(self.median_playtime_minutes / 60.0, 1)

    def __str__(self) -> str:
        return f"{self.game.name} · {self.median_hours}h"
