import math
from data_models import SituationActuelle, NouveauProjet, PremierBien
from typing import Optional

def mensualite_credit(capital, taux_annuel, duree_annees):
    """Calcule la mensualité d'un prêt amortissable (hors assurance)."""
    if capital <= 0:
        return 0
    n = duree_annees * 12
    i = taux_annuel / 100 / 12
    if i == 0:
        return capital / n
    return capital * i / (1 - (1 + i) ** -n)

def calcul_ratios(situation: SituationActuelle, premier_bien: Optional[PremierBien] = None, projet: Optional[NouveauProjet] = None):
    """Calcule taux d'endettement, taux d'effort et reste à vivre."""
    # Revenus de base
    revenus_salaires = situation.revenus_mensuels
    charges_fixes = situation.charges_mensuelles
    mensualites_autres_credits = situation.credits_mensuels

    # Premier bien existant
    mensualite_premier_bien = 0
    loyer_premier_bien = 0
    if premier_bien:
        mensualite_premier_bien = premier_bien.mensualite_actuelle
        loyer_premier_bien = premier_bien.loyer_percu

    # Nouveau projet
    mensualite_nouveau = 0
    loyer_nouveau = 0
    if projet:
        capital = projet.prix_bien - projet.apport
        mensualite_nouveau = mensualite_credit(capital, projet.taux_nominal, projet.duree_annees)
        loyer_nouveau = projet.loyer_attendu

    # Totaux
    revenus_totaux = revenus_salaires + loyer_premier_bien + loyer_nouveau
    mensualites_immobilier = mensualite_premier_bien + mensualite_nouveau
    mensualites_totales = mensualites_immobilier + mensualites_autres_credits

    # Calculs des taux
    taux_endettement = mensualites_totales / revenus_totaux if revenus_totaux > 0 else 0
    taux_effort = mensualites_totales / revenus_salaires if revenus_salaires > 0 else 0
    reste_a_vivre = revenus_totaux - mensualites_totales - charges_fixes

    return {
        "revenus_salaires": revenus_salaires,
        "revenus_locatifs": loyer_premier_bien + loyer_nouveau,
        "revenus_totaux": revenus_totaux,
        "mensualite_premier_bien": mensualite_premier_bien,
        "mensualite_nouveau": mensualite_nouveau,
        "mensualites_immobilier": mensualites_immobilier,
        "mensualites_autres_credits": mensualites_autres_credits,
        "mensualites_totales": mensualites_totales,
        "taux_endettement": taux_endettement,
        "taux_effort": taux_effort,
        "reste_a_vivre": reste_a_vivre,
    }