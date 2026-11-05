import logging
from collections.abc import Iterable

from geography.models import Country, GoogleTrendsInterest
from ingestion.sources.google_trends.trends_record import TrendsRecord

logger = logging.getLogger(__name__)
BATCH_SIZE = 500


def save_trends_records(records: Iterable[TrendsRecord]) -> int:
    """Enregistre ou met à jour les scores Trends en base."""
    valid_records = list(records)
    if not valid_records:
        return 0

    country_map = {c.iso2: c for c in Country.objects.all()}
    objects_to_create: list[GoogleTrendsInterest] = []

    for rec in valid_records:
        country = country_map.get(rec.iso2)
        if not country:
            continue
        objects_to_create.append(
            GoogleTrendsInterest(
                game_id=rec.appid,
                country=country,
                date=rec.date,
                interest=rec.interest,
            )
        )

    if not objects_to_create:
        return 0

    GoogleTrendsInterest.objects.bulk_create(
        objects_to_create,
        update_conflicts=True,
        unique_fields=["game", "country", "date"],
        update_fields=["interest"],
        batch_size=BATCH_SIZE,
    )
    return len(objects_to_create)
