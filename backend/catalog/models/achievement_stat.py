from django.db import models

PERCENT_DIGITS = 5
PERCENT_DECIMALS = 2


class AchievementStat(models.Model):
    """Part des joueurs d'un jeu qui ont débloqué un succès (Steam Web API, T-35)."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="achievements")
    name = models.CharField(max_length=128)
    display_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    percent = models.DecimalField(max_digits=PERCENT_DIGITS, decimal_places=PERCENT_DECIMALS)
    date = models.DateField()

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["game", "name"], name="unique_achievement_stat"),
        )
        ordering = ("game", "-percent")

    def __str__(self) -> str:
        return f"{self.game_id} · {self.display_name or self.name} · {self.percent} %"
