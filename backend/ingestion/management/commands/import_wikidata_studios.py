from argparse import ArgumentParser

from django.core.management.base import BaseCommand

from ingestion.http import ApiError
from ingestion.import_tracking import tracked_import
from ingestion.sources.top_games import most_owned_appids
from ingestion.sources.wikidata import WikidataClient, build_wikidata_client
from ingestion.sources.wikidata.studio_writer import save_studios

SOURCE = "wikidata"
DEFAULT_LIMIT = 5000


def build_client() -> WikidataClient:
    return build_wikidata_client()


class Command(BaseCommand):
    help = (
        "Importe depuis Wikidata (SPARQL, sans clé) les studios des jeux les plus possédés et le "
        "pays de chaque studio. Complète les pays IGDB sans jamais les remplacer."
    )

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="nombre de jeux")

    def handle(self, *args: object, **options: object) -> None:
        with tracked_import(SOURCE) as report:
            try:
                studios = build_client().studios(most_owned_appids(options["limit"]))
            except ApiError as error:
                report.add_error(str(error))
                return
            report.rows = save_studios(studios)
        self.stdout.write(
            f"Wikidata : {report.rows} liens jeu → studio, {len(report.errors)} erreur(s)."
        )
