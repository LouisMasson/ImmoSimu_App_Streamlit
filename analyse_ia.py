
import openai
import os
from typing import Optional
from data_models import SituationActuelle, NouveauProjet, PremierBien

def analyser_projet_avec_ia(resultats: dict, situation: SituationActuelle, premier_bien: Optional[PremierBien] = None, projet: Optional[NouveauProjet] = None) -> str:
    """
    Analyse le projet immobilier avec OpenAI GPT-4o en tant que conseiller patrimonial.
    """
    
    # Récupérer la clé API depuis les secrets
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ Erreur : Clé API OpenAI non configurée. Veuillez ajouter OPENAI_API_KEY dans les secrets."
    
    # Validation basique de la clé API
    if not api_key.startswith('sk-') or len(api_key) < 40:
        return "❌ Erreur : Format de clé API OpenAI invalide."
    
    # Configurer le client OpenAI
    client = openai.OpenAI(api_key=api_key)
    
    # Préparer les données du projet pour l'analyse
    contexte_projet = f"""
SITUATION FINANCIÈRE ACTUELLE :
- Revenus salaires mensuels : {resultats['revenus_salaires']:,.0f} €
- Revenus locatifs mensuels : {resultats['revenus_locatifs']:,.0f} €
- Revenus totaux mensuels : {resultats['revenus_totaux']:,.0f} €
- Charges mensuelles : Non détaillé
- Mensualités autres crédits : {resultats['mensualites_autres_credits']:,.0f} €
- Nombre de personnes dans le foyer : {situation.personnes_foyer}

PREMIER BIEN EXISTANT :
"""
    
    if premier_bien:
        contexte_projet += f"""- Prix d'achat : {premier_bien.prix_achat:,.0f} €
- Mensualité actuelle : {premier_bien.mensualite_actuelle:,.0f} €
- Loyer perçu : {premier_bien.loyer_percu:,.0f} €
"""
        if resultats.get('anciennete_pret_annees', 0) > 0:
            contexte_projet += f"""- Ancienneté du prêt : {resultats['anciennete_pret_annees']:.1f} ans
- Durée restante : {resultats['duree_restante_annees']:.1f} ans
"""
    else:
        contexte_projet += "- Aucun bien immobilier existant\n"
    
    contexte_projet += f"""
NOUVEAU PROJET :
"""
    
    if projet:
        contexte_projet += f"""- Prix du bien : {projet.prix_bien:,.0f} €
- Apport personnel : {projet.apport:,.0f} €
- Taux nominal : {projet.taux_nominal}%
- Durée du prêt : {projet.duree_annees} ans
- Loyer attendu : {projet.loyer_attendu:,.0f} €
- Mensualité calculée : {resultats['mensualite_nouveau']:,.0f} €
"""
    else:
        contexte_projet += "- Aucun nouveau projet défini\n"
    
    contexte_projet += f"""
INDICATEURS CALCULÉS :
- Taux d'endettement : {resultats['taux_endettement']*100:.1f}% (seuil bancaire : 35%)
- Taux d'effort : {resultats['taux_effort']*100:.1f}%
- Reste à vivre : {resultats['reste_a_vivre']:,.0f} € (minimum recommandé : {800 * situation.personnes_foyer:,.0f} €)
- Total mensualités : {resultats['mensualites_totales']:,.0f} €
"""
    
    # Ajouter les détails par porteur si applicable
    if resultats.get('details_porteurs'):
        contexte_projet += "\nDÉTAIL PAR PORTEUR DU PROJET :\n"
        for detail in resultats['details_porteurs']:
            contexte_projet += f"""
- {detail['nom']} ({detail['pourcentage']}% du projet) :
  * Revenus salaires : {detail['revenus_salaires']:,.0f} €
  * Taux d'endettement : {detail['taux_endettement']*100:.1f}%
  * Taux d'effort : {detail['taux_effort']*100:.1f}%
  * Reste à vivre : {detail['reste_a_vivre']:,.0f} €
"""
    
    # Prompt pour l'IA
    prompt = f"""Tu es un conseiller patrimonial expérimenté spécialisé dans l'investissement immobilier et le financement. 

Analyse le projet immobilier suivant et fournis une analyse détaillée et des recommandations :

{contexte_projet}

Ton analyse doit être TRÈS CONCISE et inclure :

1. **ÉVALUATION** : Faisabilité (1-2 phrases)
2. **POINTS CLÉS** : Principal atout et principal risque
3. **CONSEIL PRIORITAIRE** : 1 recommandation essentielle

Sois précis, professionnel et bienveillant. Utilise des emojis.
IMPÉRATIF : Limite ta réponse à 500 caractères maximum (environ 80-100 mots).
"""
    
    try:
        # Appel à l'API OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "Tu es un conseiller patrimonial expert, rigoureux et pédagogue. Tu analyses les projets immobiliers avec une approche professionnelle et donnes des conseils adaptés à chaque situation."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0.7,
            timeout=30.0
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Erreur lors de l'analyse IA : {str(e)}\n\nVérifiez que votre clé API OpenAI est valide et que vous avez du crédit disponible."
