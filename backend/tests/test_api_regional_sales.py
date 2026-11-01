import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from geography.models import RegionalSales


@pytest.mark.django_db
def test_regional_sales_stats_fallback():
    client = APIClient()
    url = reverse("stats-regional-sales")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert "by_genre" in data
    assert "top_regions" in data
    assert len(data["by_genre"]) >= 1


@pytest.mark.django_db
def test_regional_sales_stats_with_data():
    RegionalSales.objects.create(
        name="Pokemon Red",
        genre="Role-Playing",
        na_sales=11.27,
        eu_sales=8.89,
        jp_sales=10.22,
        other_sales=1.0,
    )
    client = APIClient()
    url = reverse("stats-regional-sales")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data["by_genre"]) == 1
    assert data["by_genre"][0]["genre"] == "Role-Playing"
    assert data["by_genre"][0]["jp"] == 10.2
