"""Pays connus des imports : ISO-2, ISO-3, ISO numérique (IGDB), nom français, continent.

Les pays de prix du Store (T-10) et les principaux pays de studios (T-11, T-26). Un pays
absent d'ici se crée à la main dans l'admin ; `ensure_countries` ne réécrit jamais une ligne.
"""

from typing import NamedTuple

from geography.models import Country


class CountryRow(NamedTuple):
    iso2: str
    iso3: str
    numeric: int
    name_fr: str
    continent: str


EUROPE, ASIA, AFRICA, OCEANIA = "Europe", "Asie", "Afrique", "Océanie"
NORTH_AMERICA, SOUTH_AMERICA = "Amérique du Nord", "Amérique du Sud"

COUNTRIES: tuple[CountryRow, ...] = (
    CountryRow("AE", "ARE", 784, "Émirats arabes unis", ASIA),
    CountryRow("AR", "ARG", 32, "Argentine", SOUTH_AMERICA),
    CountryRow("AT", "AUT", 40, "Autriche", EUROPE),
    CountryRow("AU", "AUS", 36, "Australie", OCEANIA),
    CountryRow("BE", "BEL", 56, "Belgique", EUROPE),
    CountryRow("BG", "BGR", 100, "Bulgarie", EUROPE),
    CountryRow("BR", "BRA", 76, "Brésil", SOUTH_AMERICA),
    CountryRow("BY", "BLR", 112, "Biélorussie", EUROPE),
    CountryRow("CA", "CAN", 124, "Canada", NORTH_AMERICA),
    CountryRow("CH", "CHE", 756, "Suisse", EUROPE),
    CountryRow("CL", "CHL", 152, "Chili", SOUTH_AMERICA),
    CountryRow("CN", "CHN", 156, "Chine", ASIA),
    CountryRow("CO", "COL", 170, "Colombie", SOUTH_AMERICA),
    CountryRow("CR", "CRI", 188, "Costa Rica", NORTH_AMERICA),
    CountryRow("CY", "CYP", 196, "Chypre", EUROPE),
    CountryRow("CZ", "CZE", 203, "Tchéquie", EUROPE),
    CountryRow("DE", "DEU", 276, "Allemagne", EUROPE),
    CountryRow("DK", "DNK", 208, "Danemark", EUROPE),
    CountryRow("EE", "EST", 233, "Estonie", EUROPE),
    CountryRow("EG", "EGY", 818, "Égypte", AFRICA),
    CountryRow("ES", "ESP", 724, "Espagne", EUROPE),
    CountryRow("FI", "FIN", 246, "Finlande", EUROPE),
    CountryRow("FR", "FRA", 250, "France", EUROPE),
    CountryRow("GB", "GBR", 826, "Royaume-Uni", EUROPE),
    CountryRow("GR", "GRC", 300, "Grèce", EUROPE),
    CountryRow("HK", "HKG", 344, "Hong Kong", ASIA),
    CountryRow("HR", "HRV", 191, "Croatie", EUROPE),
    CountryRow("HU", "HUN", 348, "Hongrie", EUROPE),
    CountryRow("ID", "IDN", 360, "Indonésie", ASIA),
    CountryRow("IE", "IRL", 372, "Irlande", EUROPE),
    CountryRow("IL", "ISR", 376, "Israël", ASIA),
    CountryRow("IN", "IND", 356, "Inde", ASIA),
    CountryRow("IS", "ISL", 352, "Islande", EUROPE),
    CountryRow("IT", "ITA", 380, "Italie", EUROPE),
    CountryRow("JP", "JPN", 392, "Japon", ASIA),
    CountryRow("KR", "KOR", 410, "Corée du Sud", ASIA),
    CountryRow("KW", "KWT", 414, "Koweït", ASIA),
    CountryRow("KZ", "KAZ", 398, "Kazakhstan", ASIA),
    CountryRow("LT", "LTU", 440, "Lituanie", EUROPE),
    CountryRow("LU", "LUX", 442, "Luxembourg", EUROPE),
    CountryRow("LV", "LVA", 428, "Lettonie", EUROPE),
    CountryRow("MA", "MAR", 504, "Maroc", AFRICA),
    CountryRow("MT", "MLT", 470, "Malte", EUROPE),
    CountryRow("MX", "MEX", 484, "Mexique", NORTH_AMERICA),
    CountryRow("MY", "MYS", 458, "Malaisie", ASIA),
    CountryRow("NG", "NGA", 566, "Nigeria", AFRICA),
    CountryRow("NL", "NLD", 528, "Pays-Bas", EUROPE),
    CountryRow("NO", "NOR", 578, "Norvège", EUROPE),
    CountryRow("NZ", "NZL", 554, "Nouvelle-Zélande", OCEANIA),
    CountryRow("PE", "PER", 604, "Pérou", SOUTH_AMERICA),
    CountryRow("PH", "PHL", 608, "Philippines", ASIA),
    CountryRow("PK", "PAK", 586, "Pakistan", ASIA),
    CountryRow("PL", "POL", 616, "Pologne", EUROPE),
    CountryRow("PT", "PRT", 620, "Portugal", EUROPE),
    CountryRow("QA", "QAT", 634, "Qatar", ASIA),
    CountryRow("RO", "ROU", 642, "Roumanie", EUROPE),
    CountryRow("RS", "SRB", 688, "Serbie", EUROPE),
    CountryRow("RU", "RUS", 643, "Russie", EUROPE),
    CountryRow("SA", "SAU", 682, "Arabie saoudite", ASIA),
    CountryRow("SE", "SWE", 752, "Suède", EUROPE),
    CountryRow("SG", "SGP", 702, "Singapour", ASIA),
    CountryRow("SI", "SVN", 705, "Slovénie", EUROPE),
    CountryRow("SK", "SVK", 703, "Slovaquie", EUROPE),
    CountryRow("TH", "THA", 764, "Thaïlande", ASIA),
    CountryRow("TR", "TUR", 792, "Turquie", ASIA),
    CountryRow("TW", "TWN", 158, "Taïwan", ASIA),
    CountryRow("UA", "UKR", 804, "Ukraine", EUROPE),
    CountryRow("US", "USA", 840, "États-Unis", NORTH_AMERICA),
    CountryRow("UY", "URY", 858, "Uruguay", SOUTH_AMERICA),
    CountryRow("VN", "VNM", 704, "Viêt Nam", ASIA),
    CountryRow("ZA", "ZAF", 710, "Afrique du Sud", AFRICA),
)

BY_ISO2 = {row.iso2: row for row in COUNTRIES}
BY_NUMERIC = {row.numeric: row for row in COUNTRIES}


def ensure_countries(iso2_codes: set[str]) -> set[str]:
    """Crée les pays connus de la table qui manquent ; renvoie les codes présents en base."""
    wanted = {code.upper() for code in iso2_codes}
    Country.objects.bulk_create(
        [
            Country(iso2=row.iso2, iso3=row.iso3, name_fr=row.name_fr, continent=row.continent)
            for code in wanted
            if (row := BY_ISO2.get(code))
        ],
        ignore_conflicts=True,
    )
    return set(Country.objects.filter(iso2__in=wanted).values_list("iso2", flat=True))
