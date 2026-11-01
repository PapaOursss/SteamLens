from django.db import models


class Company(models.Model):
    """Studio ou éditeur ; son pays sert aux cartes des studios."""

    name = models.CharField(max_length=255, unique=True)
    country = models.ForeignKey(
        "geography.Country",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.name
