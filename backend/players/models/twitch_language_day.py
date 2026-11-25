from django.db import models


class TwitchLanguageDay(models.Model):
    """Heures regardées dans une langue de stream, pour une catégorie et un jour.

    Chaque relevé horaire ajoute ses spectateurs : la somme sur la journée vaut des heures
    regardées. Elle nourrit la carte des genres par pays (T-23).
    """

    category = models.ForeignKey(
        "players.TwitchCategory", on_delete=models.CASCADE, related_name="language_days"
    )
    day = models.DateField(db_index=True)
    language = models.CharField(max_length=16)
    viewer_hours = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["category", "day", "language"], name="unique_twitch_language_day"
            ),
        )
        ordering = ("-day", "-viewer_hours")

    def __str__(self) -> str:
        return f"{self.day} · {self.category_id} · {self.language} · {self.viewer_hours} h"
