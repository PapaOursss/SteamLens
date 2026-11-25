"""Mots vides retirés des nuages de mots des avis (T-40), par langue de l'API Steam.

« game », « jeu », « play »… sont aussi retirés : ils sont en tête des deux nuages et ne disent
rien de ce qui plaît ou déplaît.
"""


def _word_set(words: str) -> frozenset[str]:
    return frozenset(words.split())


ENGLISH_STOPWORDS = _word_set(
    """
    about above after again against all also although always am among an and another any anyone
    anything are aren around because been before being below between both but can cannot could
    couldn did didn does doesn doing don done down during each either else even ever every few
    for from further get gets getting got had hadn has hasn have haven having her here hers
    herself him himself his how however into isn its itself just let like ll made make makes
    many may more most much must myself need never new nor not now off once one only other our
    ours ourselves out over own really same say she should shouldn since some something still
    such than that the their theirs them themselves then there these they thing things this
    those though through too under until upon very was wasn way well were weren what when where
    whether which while who whom why will with without won would wouldn yet you your yours
    yourself yourselves the and for are but not you all any can had her was one our out has his
    how its may new now see two who did get let put say she too use dont cant isnt didnt doesnt
    wont thats youre ive its im lot lots bit give gives want wants going game games play played
    playing plays player players steam review reviews hours hour time
    """
)

FRENCH_STOPWORDS = _word_set(
    """
    alors après assez au aucun aucune aujourd aussi autre autres aux avant avec avoir bah bien
    car ce ceci cela celle celles celui cependant certains ces cet cette ceux chaque chez
    comme comment dans de des donc dont du elle elles en encore entre est et étaient était
    étant été être eu eux fait faire fais fois font hors ici il ils je jusqu juste la le les
    leur leurs lui là ma mais me même mêmes mes moi moins mon ne ni nos notre nous on ont ou où
    par parce pas peu peut peut-être plupart plus pour pourquoi qu quand que quel quelle
    quelles quels qui sa sans se sera ses seulement si sien son sont sous soyez sur ta tant te
    tes toi ton tous tout toute toutes très trop tu un une vos votre vous vraiment ça déjà
    avez avons aurait aura aurais avais avait c d j l m n s t y suis es sommes êtes serait
    sont faut fait faites rien tellement quoi oui non via dire dit chose choses beaucoup
    jeu jeux jouer joue joué jouez jouable joueur joueurs heures heure temps steam avis
    """
)

STOPWORDS_BY_LANGUAGE: dict[str, frozenset[str]] = {
    "english": ENGLISH_STOPWORDS,
    "french": FRENCH_STOPWORDS,
}
