from django.db import models


class Country(models.Model):
    """Pays au format ISO : l'ISO-3 sert de clé aux cartes ECharts."""

    iso2 = models.CharField(max_length=2, primary_key=True)
    iso3 = models.CharField(max_length=3, unique=True)
    name_fr = models.CharField(max_length=100)
    continent = models.CharField(max_length=32, blank=True)
    main_language = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ("name_fr",)
        verbose_name_plural = "countries"

    def __str__(self) -> str:
        return self.name_fr
