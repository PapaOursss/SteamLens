import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from ingestion.models import ImportRun

logger = logging.getLogger(__name__)


@dataclass
class ImportReport:
    """Ce qu'un import a fait : lignes écrites et erreurs non bloquantes."""

    rows: int = 0
    errors: list[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        logger.warning(message)
        self.errors.append(message)


@contextmanager
def tracked_import(source: str) -> Iterator[ImportReport]:
    """Trace l'import dans `ImportRun` : début, fin, lignes et erreurs, même s'il plante."""
    run = ImportRun.objects.create(source=source)
    report = ImportReport()
    try:
        yield report
    except Exception as error:
        report.add_error(f"Import interrompu : {error!r}")
        raise
    finally:
        run.finish(rows=report.rows, errors="\n".join(report.errors))
