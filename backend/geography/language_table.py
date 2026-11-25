"""Langues des avis Steam parlées dans chaque pays de `country_table` (T-23).

Part approximative des habitants rattachés à chaque langue, langue principale d'abord. Un pays
dont la langue n'est pas suivie par l'import des avis est absent : mieux vaut un blanc.
"""

COUNTRY_LANGUAGES: dict[str, dict[str, float]] = {
    "US": {"english": 0.85, "spanish": 0.15},
    "GB": {"english": 1.0},
    "IE": {"english": 1.0},
    "AU": {"english": 1.0},
    "NZ": {"english": 1.0},
    "CA": {"english": 0.78, "french": 0.22},
    "ZA": {"english": 1.0},
    "FR": {"french": 1.0},
    "BE": {"french": 1.0},
    "LU": {"french": 0.7, "german": 0.3},
    "CH": {"german": 0.7, "french": 0.3},
    "DE": {"german": 1.0},
    "AT": {"german": 1.0},
    "ES": {"spanish": 1.0},
    "MX": {"spanish": 1.0},
    "AR": {"spanish": 1.0},
    "CL": {"spanish": 1.0},
    "CO": {"spanish": 1.0},
    "CR": {"spanish": 1.0},
    "PE": {"spanish": 1.0},
    "UY": {"spanish": 1.0},
    "BR": {"brazilian": 1.0},
    "RU": {"russian": 1.0},
    "BY": {"russian": 1.0},
    "KZ": {"russian": 1.0},
    "PL": {"polish": 1.0},
    "TR": {"turkish": 1.0},
    "CN": {"schinese": 1.0},
    "JP": {"japanese": 1.0},
    "KR": {"koreana": 1.0},
}
