from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.test import Client, TestCase

from catalog.models import Game
from ingestion.sources.steamcharts.csv_history_parser import parse_player_history_csv
from players.models import PlayerCountSnapshot

FIXTURE_CSV = Path(__file__).parent / "fixtures" / "steamcharts" / "sample_player_history.csv"


class MonthlyPlayerRaceTests(TestCase):
    def test_parse_player_history_csv(self) -> None:
        records = parse_player_history_csv(FIXTURE_CSV)
        assert len(records) == 15
        rec_cs = records[0]
        assert rec_cs.appid == 730
        assert rec_cs.name == "Counter-Strike 2"
        assert rec_cs.avg_players == 501000
        assert rec_cs.peak_players == 817000
        assert rec_cs.month_date.year == 2020
        assert rec_cs.month_date.month == 1

    def test_import_command(self) -> None:
        out = StringIO()
        call_command("import_player_history_csv", str(FIXTURE_CSV), stdout=out)
        assert PlayerCountSnapshot.objects.filter(source="steamcharts_monthly_csv").count() == 15
        assert Game.objects.filter(appid=730).exists()

    def test_api_empty_returns_mock_data(self) -> None:
        client = Client()
        res = client.get("/api/stats/monthly-player-race/")
        assert res.status_code == 200
        data = res.json()
        assert "months" in data
        assert "timeline" in data
        assert len(data["months"]) > 0

    def test_api_with_real_snapshots(self) -> None:
        game1 = Game.objects.create(appid=730, name="CS2")
        game2 = Game.objects.create(appid=570, name="Dota")

        d1 = datetime(2021, 1, 1, tzinfo=UTC)
        d2 = datetime(2021, 2, 1, tzinfo=UTC)

        PlayerCountSnapshot.objects.create(game=game1, taken_at=d1, players=1000, source="test")
        PlayerCountSnapshot.objects.create(game=game2, taken_at=d1, players=800, source="test")
        PlayerCountSnapshot.objects.create(game=game1, taken_at=d2, players=1200, source="test")
        PlayerCountSnapshot.objects.create(game=game2, taken_at=d2, players=700, source="test")

        client = Client()
        res = client.get("/api/stats/monthly-player-race/")
        assert res.status_code == 200
        data = res.json()
        assert data["months"] == ["2021-01", "2021-02"]
        assert len(data["timeline"]["2021-01"]) == 2
        assert data["timeline"]["2021-01"][0]["appid"] == 730
