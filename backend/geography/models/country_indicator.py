from django.db import models


class CountryIndicator(models.Model):
    """Dernière valeur connue d'un indicateur de la Banque mondiale pour un pays (T-25)."""

    GDP_PER_CAPITA = "NY.GDP.PCAP.PP.CD"
    POPULATION = "SP.POP.TOTL"

    country = models.ForeignKey(
        "geography.Country", on_delete=models.CASCADE, related_name="indicators"
    )
    indicator = models.CharField(max_length=32)
    year = models.PositiveSmallIntegerField()
    value = models.FloatField()

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=["country", "indicator"], name="unique_country_indicator"
            ),
        )

    def __str__(self) -> str:
        return f"{self.country_id} · {self.indicator} · {self.year} : {self.value}"
