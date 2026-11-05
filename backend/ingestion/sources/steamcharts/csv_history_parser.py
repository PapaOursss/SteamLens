import csv
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple


class MonthlyPlayerRecord(NamedTuple):
    appid: int
    name: str
    month_date: datetime
    avg_players: int
    peak_players: int


def parse_player_history_csv(file_path: Path, limit: int | None = None) -> list[MonthlyPlayerRecord]:
    """Lit un fichier CSV d'historique mensuel Kaggle / SteamCharts."""
    records: list[MonthlyPlayerRecord] = []
    with file_path.open(encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for count, row in enumerate(reader):
            if limit and count >= limit:
                break
            try:
                month_str = row.get("month", "").strip()
                # Format YYYY-MM ou YYYY-MM-DD
                if len(month_str) == 7:
                    dt = datetime.strptime(month_str, "%Y-%m").replace(tzinfo=UTC)
                else:
                    dt = datetime.strptime(month_str[:10], "%Y-%m-%d").replace(tzinfo=UTC)

                appid = int(row.get("appid", 0))
                name = row.get("game_name", "").strip() or f"App {appid}"
                avg_p = int(float(row.get("avg_players", 0)))
                peak_p = int(float(row.get("peak_players", 0)))

                records.append(
                    MonthlyPlayerRecord(
                        appid=appid,
                        name=name,
                        month_date=dt,
                        avg_players=avg_p,
                        peak_players=peak_p,
                    )
                )
            except (ValueError, KeyError):
                continue
    return records
