from django.db import models


class ProfileSample(models.Model):
    """Taille de l'échantillon de profils publics lus pour un jeu à une date (T-37).

    Des comptes seulement : aucun SteamID ni pseudo n'est enregistré.
    """

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="profile_samples"
    )
    date = models.DateField()
    profiles = models.PositiveIntegerField(default=0)
    without_country = models.PositiveIntegerField(default=0)
    # Pays déclaré mais absent de `geography.country_table` : compté, pas cartographié.
    unmapped_country = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=["game", "date"], name="unique_profile_sample"),
        )
        ordering = ("-date",)

    def __str__(self) -> str:
        return f"{self.game_id} · {self.profiles} profils · {self.date}"
