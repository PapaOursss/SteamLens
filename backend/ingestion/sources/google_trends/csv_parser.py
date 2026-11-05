import csv
from datetime import date

from ingestion.sources.google_trends.trends_record import TrendsRecord


def parse_trends_csv(
    content: str, appid: int, snapshot_date: date, country_code_map: dict[str, str] | None = None
) -> list[TrendsRecord]:
    """Lit un export CSV de Google Trends (« Intérêt par région »).

    Google Trends formate l'en-tête avec les métadonnées sur plusieurs lignes :
    Catégorie : Toutes les catégories
    Région, <mot clé>: (<période>)
    France, 100
    ...
    """
    lines = content.strip().splitlines()
    data_lines: list[str] = []
    header_found = False

    for line in lines:
        if not header_found:
            # L'en-tête réel contient Région/Region ou Pays/Country
            if any(term in line.lower() for term in ("région", "region", "pays", "country")):
                header_found = True
                data_lines.append(line)
        else:
            if line.strip():
                data_lines.append(line)

    if not data_lines:
        return []

    records: list[TrendsRecord] = []
    reader = csv.reader(data_lines)
    next(reader, None)  # Saute l'en-tête

    codes = country_code_map or {}

    for row in reader:
        if len(row) < 2:
            continue
        country_name = row[0].strip()
        raw_val = row[1].strip().replace("<", "").replace("%", "")
        if not raw_val or not raw_val.isdigit():
            continue
        interest = int(raw_val)

        # Résolution iso2
        iso2 = codes.get(country_name)
        if not iso2:
            # Si le nom fait 2 lettres et est majuscule, c'est déjà un code iso2
            if len(country_name) == 2 and country_name.isupper():
                iso2 = country_name
            else:
                continue

        records.append(
            TrendsRecord(
                appid=appid,
                iso2=iso2,
                date=snapshot_date,
                interest=interest,
            )
        )
    return records
