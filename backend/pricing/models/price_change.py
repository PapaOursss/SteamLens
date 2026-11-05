from django.db import models

from pricing.models.price_point import PRICE_DECIMALS, PRICE_DIGITS


class PriceChange(models.Model):
    """Un changement de prix d'un jeu sur Steam, d'après IsThereAnyDeal (T-18).

    `regular` est le prix hors promo au même moment ; `cut` la remise en pourcentage.
    """

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="price_changes")
    country = models.ForeignKey(
        "geography.Country", on_delete=models.PROTECT, related_name="price_changes"
    )
    changed_at = models.DateTimeField()
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=PRICE_DIGITS, decimal_places=PRICE_DECIMALS)
    regular = models.DecimalField(max_digits=PRICE_DIGITS, decimal_places=PRICE_DECIMALS)
    cut = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "country", "changed_at"], name="unique_price_change"
            ),
        )
        ordering = ("changed_at",)

    def __str__(self) -> str:
        return f"{self.game_id} · {self.changed_at:%Y-%m-%d} · {self.price} {self.currency}"
