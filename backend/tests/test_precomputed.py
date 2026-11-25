from unittest.mock import patch

import pytest
from django.utils import timezone

from catalog.precomputed import precomputed
from ingestion.models import ImportRun


@pytest.mark.django_db
def test_rebuilt_only_after_a_catalog_import(settings, tmp_path):
    settings.PRECOMPUTED_DIR = tmp_path
    calls = []

    def build():
        calls.append(1)
        return {"calls": len(calls)}

    with patch("catalog.precomputed.database_version", return_value=1):
        assert precomputed("x", build) == {"calls": 1}
        assert precomputed("x", build) == {"calls": 1}
        ImportRun.objects.create(source="snapshot_players", finished_at=timezone.now())
        assert precomputed("x", build) == {"calls": 1}
        ImportRun.objects.create(source="steamspy", finished_at=timezone.now())
        assert precomputed("x", build) == {"calls": 2}
