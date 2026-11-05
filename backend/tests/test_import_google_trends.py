from datetime import date
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase

from catalog.models import Game
from geography.models import Country, GoogleTrendsInterest
from ingestion.sources.google_trends import (
    TrendsRecord,
    parse_trends_csv,
    save_trends_records,
)

FIXTURE_CSV = Path(__file__).parent / "fixtures" / "google_trends" / "sample_trends.csv"


class GoogleTrendsImportTests(TestCase):
    def setUp(self) -> None:
        self.game = Game.objects.create(appid=892970, name="Valheim", owners_mid=5000000)
        self.country_fr = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
        self.country_us = Country.objects.create(iso2="US", iso3="USA", name_fr="États-Unis")
        self.today = date(2026, 11, 5)

    def test_parse_trends_csv(self) -> None:
        content = FIXTURE_CSV.read_text(encoding="utf-8")
        mapping = {"France": "FR", "États-Unis": "US"}
        records = parse_trends_csv(content, appid=self.game.appid, snapshot_date=self.today, country_code_map=mapping)

        assert len(records) == 2
        rec_fr = next(r for r in records if r.iso2 == "FR")
        assert rec_fr.interest == 45
        assert rec_fr.appid == 892970
        assert rec_fr.date == self.today

    def test_save_trends_records(self) -> None:
        records = [
            TrendsRecord(appid=self.game.appid, iso2="FR", date=self.today, interest=50),
            TrendsRecord(appid=self.game.appid, iso2="US", date=self.today, interest=80),
        ]
        count = save_trends_records(records)
        assert count == 2
        assert GoogleTrendsInterest.objects.count() == 2

        # Idempotence / update
        records_updated = [
            TrendsRecord(appid=self.game.appid, iso2="FR", date=self.today, interest=55),
        ]
        save_trends_records(records_updated)
        assert GoogleTrendsInterest.objects.count() == 2
        assert GoogleTrendsInterest.objects.get(country__iso2="FR").interest == 55

    def test_command_import_csv(self) -> None:
        out = StringIO()
        call_command(
            "import_google_trends",
            "--csv",
            str(FIXTURE_CSV),
            "--appid",
            str(self.game.appid),
            "--date",
            "2026-11-05",
            stdout=out,
        )
        assert GoogleTrendsInterest.objects.filter(game=self.game).exists()
        assert "Google Trends :" in out.getvalue()

    @patch("ingestion.sources.google_trends.trends_client.GoogleTrendsClient.interest_by_region")
    def test_command_import_api(self, mock_interest: MagicMock) -> None:
        mock_interest.return_value = [
            TrendsRecord(appid=self.game.appid, iso2="FR", date=self.today, interest=90),
        ]
        out = StringIO()
        call_command("import_google_trends", "--limit", "1", stdout=out)
        assert GoogleTrendsInterest.objects.filter(game=self.game, country=self.country_fr).exists()
