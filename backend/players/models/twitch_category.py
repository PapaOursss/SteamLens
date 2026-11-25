from django.db import models


class TwitchCategory(models.Model):
    """Une catégorie Twitch (un jeu, ou « Just Chatting »), reliée au jeu Steam quand il existe."""

    twitch_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=255)
    box_art_url = models.URLField(max_length=500, blank=True)
    igdb_id = models.PositiveIntegerField(null=True, blank=True)
    game = models.ForeignKey(
        "catalog.Game",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="twitch_categories",
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "twitch categories"

    def __str__(self) -> str:
        return self.name
