from django.core.management.base import BaseCommand

from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.steam_hwsurvey import SurveyClient, SurveyPageError
from players.models import HardwareShare

SOURCE = "steam_hwsurvey"


def build_client() -> SurveyClient:
    return SurveyClient()


class Command(BaseCommand):
    help = "Enquête matériel et logiciels de Steam du mois : langues, OS, GPU, RAM, VR (T-27)."

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            try:
                shares = build_client().current_survey()
            except (ApiError, SurveyPageError) as error:
                report.add_error(str(error))
                shares = []
            HardwareShare.objects.bulk_create(
                [
                    HardwareShare(
                        month=share.month,
                        category=share.category,
                        item=share.item,
                        percent=share.percent,
                    )
                    for share in shares
                ],
                update_conflicts=True,
                unique_fields=["month", "category", "item"],
                update_fields=["percent"],
            )
            report.rows = len(shares)
        self.stdout.write(f"Enquête Steam : {report.rows} parts enregistrées.")
