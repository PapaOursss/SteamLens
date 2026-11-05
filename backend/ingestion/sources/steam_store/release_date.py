from datetime import date, datetime

ENGLISH_DATE_FORMATS = ("%d %b, %Y", "%b %d, %Y", "%d %B, %Y", "%B %d, %Y")


def parse_release_date(text: str) -> date | None:
    """Lit la date de sortie du Store demandée en anglais (`l=english`).

    Renvoie None pour les dates vagues (« Coming soon », « Q3 2027 ») ou dans une autre langue.
    """
    for date_format in ENGLISH_DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), date_format).date()
        except ValueError:
            continue
    return None
