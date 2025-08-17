from pydantic import BaseModel

class SituationActuelle(BaseModel):
    revenus_mensuels: float  # salaires nets + loyers existants
    charges_mensuelles: float  # charges fixes (hors crédits)
    credits_mensuels: float  # total mensualités crédits en cours
    personnes_foyer: int = 1  # nb de personnes dans le foyer

class NouveauProjet(BaseModel):
    prix_bien: float
    apport: float
    taux_nominal: float  # en %
    duree_annees: int
    loyer_attendu: float = 0  # 0 si résidence principale