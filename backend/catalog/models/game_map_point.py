from django.db import models


class GameMapPoint(models.Model):
    """Place d'un jeu sur la carte 2D du catalogue (t-SNE des tags, T-41)."""

    game = models.OneToOneField("catalog.Game", on_delete=models.CASCADE, related_name="map_point")
    x = models.FloatField()
    y = models.FloatField()
    main_tag = models.ForeignKey(
        "catalog.Tag", null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    def __str__(self) -> str:
        return f"{self.game_id} ({self.x:.1f}, {self.y:.1f})"
