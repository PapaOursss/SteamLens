import shutil
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

import httpx
from django.conf import settings

from ingestion.api_keys import get_api_keys
from ingestion.http.api_client import USER_AGENT

DOWNLOAD_URL = "https://www.kaggle.com/api/v1/datasets/download/{dataset}"
# Les jetons « API token » récents s'envoient en Bearer, les anciennes clés en Basic.
BEARER_TOKEN_PREFIX = "KGAT_"
DOWNLOAD_TIMEOUT_SECONDS = 600.0
CHUNK_BYTES = 1 << 20


class KaggleDownloadError(Exception):
    """Le dataset n'a pas pu être téléchargé ou ne contient pas le fichier attendu."""


def dataset_file(
    dataset: str, filename: str, transport: httpx.BaseTransport | None = None
) -> Path | None:
    """Chemin local d'un fichier de dataset Kaggle, téléchargé une seule fois.

    Le fichier est rangé dans `backend/data/raw/<propriétaire>__<dataset>/` (ignoré par git) ;
    s'il y est déjà (téléchargé à la main, par exemple), rien ne part sur le réseau. None
    quand il manque et que les clés Kaggle sont absentes de `backend/.env`.
    """
    target = settings.RAW_DATA_DIR / dataset.replace("/", "__") / filename
    if target.exists():
        return target
    keys = get_api_keys("kaggle", "KAGGLE_USERNAME", "KAGGLE_KEY")
    if keys is None:
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile() as archive:
        _download(dataset, keys, archive, transport)
        _extract(archive, filename, target)
    return target


def _download(
    dataset: str, keys: dict[str, str], archive: object, transport: httpx.BaseTransport | None
) -> None:
    key = keys["KAGGLE_KEY"]
    headers = {"User-Agent": USER_AGENT}
    auth = None
    if key.startswith(BEARER_TOKEN_PREFIX):
        headers["Authorization"] = f"Bearer {key}"
    else:
        auth = httpx.BasicAuth(keys["KAGGLE_USERNAME"], key)
    url = DOWNLOAD_URL.format(dataset=dataset)
    with (
        httpx.Client(
            transport=transport,
            headers=headers,
            auth=auth,
            follow_redirects=True,
            timeout=DOWNLOAD_TIMEOUT_SECONDS,
        ) as client,
        client.stream("GET", url) as response,
    ):
        if response.is_error:
            raise KaggleDownloadError(f"{url} : HTTP {response.status_code}")
        for chunk in response.iter_bytes(CHUNK_BYTES):
            archive.write(chunk)
    archive.seek(0)


def _extract(archive: object, filename: str, target: Path) -> None:
    """Copie `filename` (cherché par son nom, quel que soit son dossier dans le zip)."""
    try:
        with zipfile.ZipFile(archive) as bundle:
            member = next(
                (name for name in bundle.namelist() if PurePosixPath(name).name == filename),
                None,
            )
            if member is None:
                raise KaggleDownloadError(f"{filename} absent de l'archive : {bundle.namelist()}")
            partial = target.with_suffix(target.suffix + ".part")
            with bundle.open(member) as source, partial.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            partial.replace(target)
    except zipfile.BadZipFile as error:
        raise KaggleDownloadError(f"archive illisible : {error}") from error
