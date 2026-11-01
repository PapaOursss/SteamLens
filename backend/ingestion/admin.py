from django.contrib import admin

from ingestion.models import ImportRun


@admin.register(ImportRun)
class ImportRunAdmin(admin.ModelAdmin):
    """Les derniers imports et leurs erreurs : la page à ouvrir quand une courbe s'arrête."""

    list_display = ("source", "started_at", "finished_at", "rows", "succeeded")
    list_filter = ("source",)
    readonly_fields = ("source", "started_at", "finished_at", "rows", "errors")
    ordering = ("-started_at",)

    @admin.display(boolean=True, description="réussi")
    def succeeded(self, import_run: ImportRun) -> bool:
        return import_run.succeeded
