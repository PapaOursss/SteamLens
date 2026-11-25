from django.core.management.base import BaseCommand

from geography.country_table import BY_ISO2, ensure_countries
from geography.models import CountryIndicator
from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.world_bank import WorldBankClient

SOURCE = "world_bank"
INDICATORS = (CountryIndicator.GDP_PER_CAPITA, CountryIndicator.POPULATION)


def build_client() -> WorldBankClient:
    return WorldBankClient()


class Command(BaseCommand):
    help = "PIB par habitant (parité de pouvoir d'achat) et population, Banque mondiale (T-25)."

    def handle(self, *args: object, **options: object) -> None:
        client = build_client()
        with tracked_import(SOURCE) as report:
            for indicator in INDICATORS:
                try:
                    report.rows += save_indicator(client, indicator)
                except ApiError as error:
                    report.add_error(str(error))
        self.stdout.write(f"Banque mondiale : {report.rows} valeurs enregistrées.")


def save_indicator(client: WorldBankClient, indicator: str) -> int:
    """Les agrégats (Afrique de l'Est, zone euro…) et pays hors table sont ignorés."""
    values = [value for value in client.latest(indicator) if value.iso2 in BY_ISO2]
    ensure_countries({value.iso2 for value in values})
    CountryIndicator.objects.bulk_create(
        [
            CountryIndicator(
                country_id=value.iso2, indicator=indicator, year=value.year, value=value.value
            )
            for value in values
        ],
        update_conflicts=True,
        unique_fields=["country", "indicator"],
        update_fields=["year", "value"],
    )
    return len(values)
