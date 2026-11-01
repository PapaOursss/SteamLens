"""Quand chaque import tourne. Une commande pas encore écrite est sautée avec un message.

Écrire un import planifié = créer la commande `manage.py` au nom prévu ici (ou changer le nom
ici dans la même pull request).
"""

from ingestion.scheduling.scheduled_command import ScheduledCommand

HOURLY = "5 * * * *"
# SteamSpy d'abord : le Store et les joueurs prennent leur top 1 000 dans ses propriétaires.
NIGHTLY = "0 2 * * *"
DAILY = "30 4 * * *"
MONTHLY = "0 5 3 * *"

SCHEDULE: tuple[ScheduledCommand, ...] = (
    ScheduledCommand("import_steamspy", NIGHTLY, "T-08"),
    ScheduledCommand("snapshot_players", HOURLY, "T-09"),
    ScheduledCommand("snapshot_twitch", HOURLY, "T-21"),
    ScheduledCommand("import_steam_store", DAILY, "T-10"),
    ScheduledCommand("import_reviews", DAILY, "T-22"),
    ScheduledCommand("import_hardware_survey", MONTHLY, "T-27"),
)
