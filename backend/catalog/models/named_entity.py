from django.db import models


class NamedEntity(models.Model):
    """Base des petites listes de référence (genre, tag, thème…) : un nom unique."""

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        abstract = True
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
