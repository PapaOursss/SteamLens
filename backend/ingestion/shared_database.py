import gzip
import hashlib
import shutil
from pathlib import Path

import httpx

SHARED_DATABASE_URL = (
    "https://github.com/PapaOursss/SteamLens/releases/download/"
    "base-2026-11-25/steamlens-base-2026-11-25.sqlite3.gz"
)
SHARED_DATABASE_SHA256 = "01ce050e05713ad3c3c4d0516914de1aad27b2b89140a34679494aa7d51bb183"
DOWNLOAD_TIMEOUT_SECONDS = 60
DOWNLOAD_ATTEMPTS = 10


class SharedDatabaseError(Exception):
    """La base partagée n'a pas pu être installée ; la base locale est intacte."""


def download_archive(url: str, archive: Path) -> str:
    """Télécharge l'archive, reprise là où une coupure l'a laissée ; renvoie son SHA-256."""
    archive.unlink(missing_ok=True)
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        try:
            _download_rest(url, archive)
            break
        except httpx.TransportError:
            if attempt == DOWNLOAD_ATTEMPTS:
                raise
    with archive.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _download_rest(url: str, archive: Path) -> None:
    received = archive.stat().st_size if archive.exists() else 0
    headers = {"Range": f"bytes={received}-"} if received else {}
    with httpx.stream(
        "GET", url, headers=headers, follow_redirects=True, timeout=DOWNLOAD_TIMEOUT_SECONDS
    ) as response:
        response.raise_for_status()
        # Un serveur qui ignore Range renvoie tout : on repart de zéro.
        resumed = response.status_code == httpx.codes.PARTIAL_CONTENT
        with archive.open("ab" if resumed else "wb") as file:
            for chunk in response.iter_raw():
                file.write(chunk)


def install_shared_database(
    database: Path, url: str = SHARED_DATABASE_URL, sha256: str = SHARED_DATABASE_SHA256
) -> None:
    """Remplace la base locale par la base partagée ; l'ancienne est gardée en « .avant »."""
    archive = database.with_name(database.name + ".telechargement")
    unpacked = database.with_name(database.name + ".nouvelle")
    try:
        if download_archive(url, archive) != sha256:
            raise SharedDatabaseError("archive incomplète ou modifiée")
        with gzip.open(archive, "rb") as source, unpacked.open("wb") as target:
            shutil.copyfileobj(source, target)
        if database.exists():
            database.replace(database.with_name(database.name + ".avant"))
        unpacked.replace(database)
    except (httpx.HTTPError, OSError) as error:
        raise SharedDatabaseError(str(error)) from error
    finally:
        archive.unlink(missing_ok=True)
        unpacked.unlink(missing_ok=True)
