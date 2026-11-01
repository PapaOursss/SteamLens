import logging

import pytest
from django.test import override_settings

from ingestion.api_keys import get_api_keys


@override_settings(API_KEYS={"TWITCH_CLIENT_ID": "id", "TWITCH_CLIENT_SECRET": "secret"})
def test_returns_the_keys_when_all_are_set() -> None:
    keys = get_api_keys("IGDB", "TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET")

    assert keys == {"TWITCH_CLIENT_ID": "id", "TWITCH_CLIENT_SECRET": "secret"}


@override_settings(API_KEYS={"STEAM_API_KEY": ""})
def test_skips_the_source_when_a_key_is_missing(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        keys = get_api_keys("Steam Web API", "STEAM_API_KEY")

    assert keys is None
    assert "Steam Web API sautée : STEAM_API_KEY" in caplog.text
