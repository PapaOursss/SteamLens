from django.db import models


class Game(models.Model):
    """Un jeu Steam. L'appid relie toutes les sources entre elles."""

    appid = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    release_date = models.DateField(null=True, blank=True)
    is_free = models.BooleanField(default=False)
    header_image = models.URLField(max_length=500, blank=True)
    igdb_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    rawg_id = models.PositiveIntegerField(null=True, blank=True, unique=True)
    itad_id = models.CharField(max_length=64, blank=True)
    # Fourchette de propriétaires estimée (SteamSpy, Kaggle) ; le milieu sert au classement.
    owners_min = models.PositiveIntegerField(null=True, blank=True)
    owners_max = models.PositiveIntegerField(null=True, blank=True)
    owners_mid = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    peak_ccu = models.PositiveIntegerField(null=True, blank=True)
    supported_languages = models.JSONField(default=list, blank=True)
    # Fiche du Steam Store (T-10).
    short_description = models.TextField(blank=True)
    screenshots = models.JSONField(default=list, blank=True)
    categories = models.JSONField(default=list, blank=True)
    minimum_requirements = models.TextField(blank=True)
    metacritic_score = models.PositiveSmallIntegerField(null=True, blank=True)
    store_fetched_at = models.DateTimeField(null=True, blank=True)
    # Date des données qui ont rempli la fiche : une source plus ancienne ne l'écrase pas.
    data_date = models.DateField(null=True, blank=True)

    genres = models.ManyToManyField("catalog.Genre", blank=True, related_name="games")
    tags = models.ManyToManyField(
        "catalog.Tag", through="catalog.GameTag", blank=True, related_name="games"
    )
    themes = models.ManyToManyField("catalog.Theme", blank=True, related_name="games")
    game_modes = models.ManyToManyField("catalog.GameMode", blank=True, related_name="games")
    platforms = models.ManyToManyField("catalog.Platform", blank=True, related_name="games")
    developers = models.ManyToManyField(
        "catalog.Company", blank=True, related_name="developed_games"
    )
    publishers = models.ManyToManyField(
        "catalog.Company", blank=True, related_name="published_games"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.appid})"
