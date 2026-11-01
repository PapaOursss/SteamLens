from django.db import models
from django.utils import timezone


class ImportRun(models.Model):
    """Trace d'un import : quand, combien de lignes, quelles erreurs."""

    source = models.CharField(max_length=64, db_index=True)
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    rows = models.PositiveIntegerField(default=0)
    errors = models.TextField(blank=True)

    class Meta:
        ordering = ("-started_at",)

    @property
    def succeeded(self) -> bool:
        return self.finished_at is not None and not self.errors

    def finish(self, rows: int, errors: str = "") -> None:
        self.finished_at = timezone.now()
        self.rows = rows
        self.errors = errors
        self.save(update_fields=["finished_at", "rows", "errors"])

    def __str__(self) -> str:
        return f"{self.source} · {self.started_at:%Y-%m-%d %H:%M}"
