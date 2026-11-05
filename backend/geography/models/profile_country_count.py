from django.db import models


class ProfileCountryCount(models.Model):
    """Nombre de profils publics d'un pays parmi les auteurs d'avis récents d'un jeu (T-37)."""

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="profile_countries"
    )
    country = models.ForeignKey(
        "geography.Country", on_delete=models.PROTECT, related_name="profile_counts"
    )
    date = models.DateField()
    profiles = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "country", "date"], name="unique_profile_country_count"
            ),
        )
        ordering = ("-date", "-profiles")

    def __str__(self) -> str:
        return f"{self.game_id} · {self.country_id} · {self.profiles} · {self.date}"
