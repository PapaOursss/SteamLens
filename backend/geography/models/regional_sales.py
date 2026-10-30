from django.db import models


class RegionalSales(models.Model):
    """Ventes historiques de jeux par région en millions d'unités (Kaggle vgsales)."""

    name = models.CharField(max_length=255, db_index=True)
    platform = models.CharField(max_length=64, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    genre = models.CharField(max_length=64, db_index=True)
    publisher = models.CharField(max_length=255, blank=True)
    na_sales = models.FloatField(default=0.0)
    eu_sales = models.FloatField(default=0.0)
    jp_sales = models.FloatField(default=0.0)
    other_sales = models.FloatField(default=0.0)

    class Meta:
        ordering = ("-na_sales",)

    @property
    def global_sales(self) -> float:
        return round(self.na_sales + self.eu_sales + self.jp_sales + self.other_sales, 2)

    def __str__(self) -> str:
        return f"{self.name} · {self.genre} · Global: {self.global_sales}M"
