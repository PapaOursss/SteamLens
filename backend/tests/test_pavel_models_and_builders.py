import datetime
from decimal import Decimal

import pytest

from catalog.models import AchievementStat, Game, ReviewWeek
from geography.models import Country, ProfileCountryCount, ProfileSample
from ingestion.management.commands import (
    import_hardware_survey,
    import_itad_history,
    import_profile_countries,
    import_reviews,
)
from ingestion.sources.itad import ItadClient
from ingestion.sources.steam_hwsurvey import SurveyClient
from ingestion.sources.steam_reviews import SteamReviewsClient
from ingestion.sources.steam_web_api import ProfileCountryClient
from players.models import HardwareShare
from pricing.models import PriceChange

DAY = datetime.date(2026, 11, 5)


@pytest.fixture
def game(db: None) -> Game:
    return Game.objects.create(appid=7, name="Jeu")


def test_model_labels(game: Game) -> None:
    france = Country.objects.create(iso2="FR", iso3="FRA", name_fr="France")
    week = ReviewWeek(game=game, week_start=DAY, positive=3, negative=1)
    assert (week.total, str(week)) == (4, "7 · semaine du 2026-11-05")
    achievement = AchievementStat(
        game=game, name="a", display_name="Fin", percent=Decimal("1.5"), date=DAY
    )
    assert str(achievement) == "7 · Fin · 1.5 %"
    assert str(ProfileSample(game=game, date=DAY, profiles=12)) == "7 · 12 profils · 2026-11-05"
    count = ProfileCountryCount(game=game, country=france, date=DAY, profiles=4)
    assert str(count) == "7 · FR · 4 · 2026-11-05"
    share = HardwareShare(month=DAY, category="os", item="Linux", percent=Decimal("3.95"))
    assert str(share) == "2026-11 · os · Linux · 3.95 %"
    change = PriceChange(game=game, changed_at=datetime.datetime(2025, 1, 2, tzinfo=datetime.UTC),
                         price=Decimal("9.99"), currency="EUR")  # fmt: skip
    assert str(change) == "7 · 2025-01-02 · 9.99 EUR"


def test_builders_make_real_clients() -> None:
    assert isinstance(import_reviews.build_client(), SteamReviewsClient)
    assert isinstance(import_hardware_survey.build_client(), SurveyClient)
    assert isinstance(import_itad_history.build_client("k"), ItadClient)
    reviews, profiles = import_profile_countries.build_clients("k")
    assert isinstance(reviews, SteamReviewsClient)
    assert isinstance(profiles, ProfileCountryClient)


def test_today_is_a_utc_date() -> None:
    for command in (import_reviews, import_profile_countries):
        assert isinstance(command.today(), datetime.date)
