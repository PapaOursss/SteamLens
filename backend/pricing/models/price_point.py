from django.db import models

PRICE_DIGITS = 10
PRICE_DECIMALS = 2


class PricePoint(models.Model):
    """Prix d'un jeu dans un pays à une date, avec sa conversion en euros."""

    game = models.ForeignKey("catalog.Game", on_delete=models.CASCADE, related_name="prices")
    country = models.ForeignKey(
        "geography.Country", on_delete=models.PROTECT, related_name="prices"
    )
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=PRICE_DIGITS, decimal_places=PRICE_DECIMALS)
    price_eur = models.DecimalField(
        max_digits=PRICE_DIGITS, decimal_places=PRICE_DECIMALS, null=True, blank=True
    )
    discount_percent = models.PositiveSmallIntegerField(default=0)
    date = models.DateField()
    source = models.CharField(max_length=32)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["game", "country", "date", "source"], name="unique_price_point"
            ),
        )
        ordering = ("date",)

    def __str__(self) -> str:
        return f"{self.game_id} · {self.country_id} · {self.price} {self.currency} · {self.date}"
