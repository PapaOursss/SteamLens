import gzip
import hashlib
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
import respx
from django.core.management import call_command
from httpx import Response

from catalog.models import Game
from ingestion.shared_database import SharedDatabaseError, install_shared_database

URL = "https://example.test/base.gz"
ARCHIVE = gzip.compress(b"nouvelle base")
SHA256 = hashlib.sha256(ARCHIVE).hexdigest()
INSTALL = "ingestion.management.commands.prepare_database.install_shared_database"


@respx.mock
def test_installs_and_keeps_previous_database(tmp_path: Path) -> None:
    respx.get(URL).mock(return_value=Response(200, content=ARCHIVE))
    database = tmp_path / "db.sqlite3"
    database.write_bytes(b"ancienne")

    install_shared_database(database, URL, SHA256)

    assert database.read_bytes() == b"nouvelle base"
    assert (tmp_path / "db.sqlite3.avant").read_bytes() == b"ancienne"
    assert len(list(tmp_path.iterdir())) == 2


@respx.mock
@pytest.mark.parametrize(
    "response", [Response(404), Response(200, content=b"tronquee")], ids=["absente", "corrompue"]
)
def test_failure_leaves_database_untouched(tmp_path: Path, response: Response) -> None:
    respx.get(URL).mock(return_value=response)
    database = tmp_path / "db.sqlite3"
    database.write_bytes(b"ancienne")

    with pytest.raises(SharedDatabaseError):
        install_shared_database(database, URL, SHA256)

    assert database.read_bytes() == b"ancienne"
    assert len(list(tmp_path.iterdir())) == 1


class CutStream(httpx.SyncByteStream):
    """Une réponse coupée au milieu."""

    def __iter__(self):
        yield ARCHIVE[:5]
        raise httpx.ReadTimeout("coupure")


@respx.mock
def test_download_resumes_after_a_cut(tmp_path: Path) -> None:
    route = respx.get(URL).mock(
        side_effect=[Response(200, stream=CutStream()), Response(206, content=ARCHIVE[5:])]
    )
    database = tmp_path / "db.sqlite3"

    install_shared_database(database, URL, SHA256)

    assert database.read_bytes() == b"nouvelle base"
    assert route.calls[1].request.headers["Range"] == "bytes=5-"


@pytest.mark.django_db
def test_database_with_games_is_kept() -> None:
    Game.objects.create(appid=1, name="Jeu")
    with patch(INSTALL) as install:
        call_command("prepare_database")
    install.assert_not_called()
