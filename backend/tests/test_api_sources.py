import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from ingestion.models import ImportRun


@pytest.mark.django_db
def test_sources_overview_empty():
    client = APIClient()
    url = reverse("sources-overview")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "pipeline" in data
    assert "sources" in data
    assert "methodology_notes" in data
    assert len(data["sources"]) == 12


@pytest.mark.django_db
def test_sources_overview_with_runs():
    client = APIClient()
    run = ImportRun.objects.create(source="steamspy", rows=100)
    run.finish(rows=100)

    url = reverse("sources-overview")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    steamspy_source = next(s for s in data["sources"] if s["key"] == "steamspy")
    assert steamspy_source["last_import"]["rows"] == 100
    assert steamspy_source["last_import"]["succeeded"] is True
