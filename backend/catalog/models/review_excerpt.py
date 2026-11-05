from django.db import models


class ReviewExcerpt(models.Model):
    """Extrait d'avis anonyme (texte seul, jamais d'auteur) pour les nuages de mots (T-40)."""

    game = models.ForeignKey(
        "catalog.Game", on_delete=models.CASCADE, related_name="review_excerpts"
    )
    text = models.TextField()
    is_positive = models.BooleanField()
    language = models.CharField(max_length=32)
    source = models.CharField(max_length=32)

    class Meta:
        ordering = ("game", "-is_positive")

    def __str__(self) -> str:
        return f"{self.game_id} · {'👍' if self.is_positive else '👎'} · {self.text[:40]}"
