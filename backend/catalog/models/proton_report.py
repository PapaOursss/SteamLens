from django.db import models


class ProtonReport(models.Model):
    """Niveau de compatibilité ProtonDB pour Linux et Steam Deck."""

    TIER_CHOICES = (
        ("native", "Native"),
        ("platinum", "Platinum"),
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("bronze", "Bronze"),
        ("borked", "Borked"),
        ("pending", "Pending"),
    )

    game = models.OneToOneField(
        "catalog.Game", on_delete=models.CASCADE, related_name="proton_report"
    )
    tier = models.CharField(max_length=16, choices=TIER_CHOICES, default="pending")
    score = models.FloatField(default=0.0)
    total_reports = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"{self.game.name} · {self.tier} ({self.total_reports} rapports)"
