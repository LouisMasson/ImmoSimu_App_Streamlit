from pydantic import BaseModel
from typing import Optional
from datetime import date

class PremierBien(BaseModel):
    prix_achat: float
    mensualite_actuelle: float
    loyer_percu: float = 0  # 0 si résidence principale
    date_achat: Optional[date] = None  # Date d'achat du bien
    duree_pret_initiale: Optional[int] = None  # Durée initiale du prêt en années

class PorteurProjet(BaseModel):
    nom: str
    revenus_mensuels: float  # salaires nets
    charges_mensuelles: float  # charges fixes personnelles
    credits_mensuels: float  # crédits personnels
    pourcentage_projet: float  # % de participation au projet (ex: 50% pour un couple)

class SituationActuelle(BaseModel):
    revenus_mensuels: float  # salaires nets uniquement
    charges_mensuelles: float  # charges fixes (hors crédits)
    credits_mensuels: float  # total mensualités crédits en cours (hors immobilier)
    personnes_foyer: int = 1  # nb de personnes dans le foyer
    porteurs: list[PorteurProjet] = []  # porteurs du projet

class NouveauProjet(BaseModel):
    prix_bien: float
    apport: float
    taux_nominal: float  # en %
    duree_annees: int
    loyer_attendu: float = 0  # 0 si résidence principale