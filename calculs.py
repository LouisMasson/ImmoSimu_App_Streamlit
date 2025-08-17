import math
from data_models import SituationActuelle, NouveauProjet

def mensualite_credit(capital, taux_annuel, duree_annees):
    """Calcule la mensualité d’un prêt amortissable (hors assurance)."""
    if capital <= 0:
        return 0
    n = duree_annees * 12
    i = taux_annuel / 100 / 12
    if i == 0:
        return capital / n
    return capital * i / (1 - (1 + i) ** -n)

def calcul_ratios(situation: SituationActuelle, projet: NouveauProjet | None = None):
    """Calcule taux d’endettement et reste à vivre avec ou sans nouveau projet."""
    revenus = situation.revenus_mensuels
    charges_fixes = situation.charges_mensuelles
    mensualites_existantes = situation.credits_mensuels

    # Ajout du projet si présent
    mensualite_nouveau = 0
    revenus_locatifs = 0
    if projet:
        capital = projet.prix_bien - projet.apport
        mensualite_nouveau = mensualite_credit(capital, projet.taux_nominal, projet.duree_annees)
        revenus_locatifs = projet.loyer_attendu

    mensualites_totales = mensualites_existantes + mensualite_nouveau
    revenus_totaux = revenus + revenus_locatifs

    taux_endettement = mensualites_totales / revenus_totaux if revenus_totaux > 0 else 0
    reste_a_vivre = revenus_totaux - mensualites_totales - charges_fixes

    return {
        "mensualite_nouveau": mensualite_nouveau,
        "taux_endettement": taux_endettement,
        "reste_a_vivre": reste_a_vivre,
    }