import streamlit as st
from data_models import SituationActuelle, NouveauProjet
from calculs import calcul_ratios

st.set_page_config(page_title="Simulation Invest Immo", layout="centered")

# --- Titre principal ---
st.title("📊 Simulateur immobilier simplifié")

st.markdown(
    "Cet outil vous aide à estimer **votre taux d’endettement** et votre **reste à vivre** "
    "si vous achetez un nouveau bien immobilier.\n\n"
    "⚠️ Résultat **indicatif** : il faudra toujours valider avec votre banquier."
)

# --- Mini tutoriel ---
with st.expander("📖 Mode d’emploi (cliquez pour afficher)", expanded=True):
    st.markdown("""
    ### ✅ Comment utiliser ce simulateur en 3 étapes :

    1. **Renseignez votre situation actuelle**  
       ➡️ Revenus nets, charges fixes et crédits en cours.

    2. **Ajoutez votre projet immobilier**  
       ➡️ Prix du bien, apport, taux, durée du prêt et éventuellement loyer attendu.

    3. **Lancez la simulation**  
       ➡️ Vous obtiendrez votre **taux d’endettement**, votre **reste à vivre** 
       et un verdict simplifié : "ça passe" ou "ça coince".

    ---
    💡 *Astuce : Vous pouvez tester plusieurs scénarios (modifier apport, durée, loyer attendu...) 
    pour voir l’impact sur votre capacité d’emprunt.*
    """)

# --- Situation actuelle ---
st.header("1. Votre situation actuelle")

revenus = st.number_input(
    "Revenus mensuels nets",
    min_value=0.0, step=100.0,
    help="Somme de vos salaires nets (après impôts et cotisations) + loyers nets déjà perçus de vos biens locatifs."
)

charges = st.number_input(
    "Charges mensuelles (hors crédits)",
    min_value=0.0, step=50.0,
    help="Vos charges fixes : alimentation, assurances, abonnements, factures, etc. ⚠️ N’incluez pas vos mensualités de prêts ici."
)

credits = st.number_input(
    "Mensualités de crédits en cours",
    min_value=0.0, step=50.0,
    help="Total des mensualités de crédits (immobilier, consommation, auto, etc.) que vous remboursez déjà."
)

personnes = st.number_input(
    "Nombre de personnes dans le foyer",
    min_value=1, step=1,
    help="Nombre total de personnes vivant dans le foyer (adulte(s) + enfants). Sert à estimer le 'reste à vivre' nécessaire."
)

situation = SituationActuelle(
    revenus_mensuels=revenus,
    charges_mensuelles=charges,
    credits_mensuels=credits,
    personnes_foyer=personnes,
)

# --- Nouveau projet ---
st.header("2. Simulation du nouveau projet")

prix = st.number_input(
    "Prix du bien (€)",
    min_value=0.0, step=1000.0,
    help="Prix d’achat du bien immobilier (hors frais de notaire et travaux)."
)

apport = st.number_input(
    "Apport personnel (€)",
    min_value=0.0, step=1000.0,
    help="Somme que vous pouvez investir immédiatement (épargne disponible)."
)

taux = st.number_input(
    "Taux nominal (%)",
    min_value=0.0, step=0.1,
    help="Taux d’intérêt proposé par la banque (hors assurance). Exemple : 3,5 %."
)

duree = st.number_input(
    "Durée du prêt (années)",
    min_value=1, max_value=30, value=20, step=1,
    help="Durée du prêt immobilier, en années. Les banques financent rarement au-delà de 25 ans."
)

loyer = st.number_input(
    "Loyer attendu (€)",
    min_value=0.0, step=50.0,
    help="Montant du loyer mensuel attendu (si investissement locatif). Saisir 0 si c’est une résidence principale."
)

projet = None
if prix > 0 and duree > 0:
    projet = NouveauProjet(
        prix_bien=prix,
        apport=apport,
        taux_nominal=taux,
        duree_annees=duree,
        loyer_attendu=loyer,
    )

# --- Résultats ---
st.header("3. Résultats de la simulation")

if st.button("Calculer"):
    resultats = calcul_ratios(situation, projet)

    st.metric("Mensualité du nouveau prêt", f"{resultats['mensualite_nouveau']:.0f} €")
    st.metric("Taux d’endettement", f"{resultats['taux_endettement']*100:.1f} %")
    st.metric("Reste à vivre", f"{resultats['reste_a_vivre']:.0f} €")

    seuil = 0.35  # 35% est la règle de référence
    reste_min = 800 * situation.personnes_foyer  # seuil simple : 800€/personne

    if resultats['taux_endettement'] <= seuil and resultats['reste_a_vivre'] >= reste_min:
        st.success(
            "✅ A priori finançable : votre taux d’endettement et reste à vivre respectent les règles bancaires habituelles.\n"
            "➡️ Vous pouvez présenter ce projet à votre banque pour validation."
        )
    else:
        st.warning(
            "⚠️ Risque de refus : soit votre taux d’endettement dépasse 35 %, "
            "soit votre reste à vivre est jugé insuffisant.\n"
            "➡️ Ajustez l’apport, la durée du prêt ou le montant du projet."
        )
