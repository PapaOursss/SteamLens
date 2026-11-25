"""Requête SPARQL : studios des jeux Steam et leur pays, d'après Wikidata.

Steam application ID (P1733) → développeur (P178) → pays, pris dans cet ordre : pays (P17),
pays d'origine (P495), pays du siège (P159 → P17), nationalité pour un développeur seul (P27).
"""

from collections.abc import Iterable

COUNTRY_PATHS = (
    ("p17", "wdt:P17"),
    ("p495", "wdt:P495"),
    ("p159", "wdt:P159/wdt:P17"),
    ("p27", "wdt:P27"),
)


def studio_query(appids: Iterable[int]) -> str:
    values = " ".join(f'"{appid}"' for appid in appids)
    optionals = "\n".join(
        f"  OPTIONAL {{ ?developer {path} ?{key} . ?{key} wdt:P297 ?{key}_iso2 ;"
        f" wdt:P298 ?{key}_iso3 . }}"
        for key, path in COUNTRY_PATHS
    )
    return f"""SELECT ?appid ?developer ?developerLabel
  {" ".join(f"?{key}_iso2 ?{key}_iso3 ?{key}Label" for key, _ in COUNTRY_PATHS)}
WHERE {{
  VALUES ?appid {{ {values} }}
  ?game wdt:P1733 ?appid ; wdt:P178 ?developer .
{optionals}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en". }}
}}"""
