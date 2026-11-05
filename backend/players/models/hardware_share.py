from django.db import models

PERCENT_DIGITS = 5
PERCENT_DECIMALS = 2


class HardwareShare(models.Model):
    """Part des joueurs Steam qui ont un matériel, un OS ou une langue, sur un mois (T-27).

    Chiffres publics de l'enquête matériel et logiciels de Steam, sans donnée personnelle.
    """

    month = models.DateField(db_index=True)
    category = models.CharField(max_length=32)
    item = models.CharField(max_length=128)
    percent = models.DecimalField(max_digits=PERCENT_DIGITS, decimal_places=PERCENT_DECIMALS)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["month", "category", "item"], name="unique_hardware_share"
            ),
        )
        ordering = ("month", "category", "-percent")

    def __str__(self) -> str:
        return f"{self.month:%Y-%m} · {self.category} · {self.item} · {self.percent} %"
