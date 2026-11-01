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
