from dataclasses import dataclass


@dataclass(frozen=True)
class ScheduledCommand:
    """Une commande `manage.py` lancée à heure fixe par le planificateur.

    `cron` suit la syntaxe crontab (minute heure jour mois jour-de-semaine).
    """

    command: str
    cron: str
    ticket: str
