import streamlit as st
from data_models import SituationActuelle, NouveauProjet, PremierBien
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
    "Revenus mensuels nets (salaires uniquement)",
    min_value=0.0, step=100.0,
    help="Vos salaires nets (après impôts et cotisations). Les loyers seront comptés séparément."
)

charges = st.number_input(
    "Charges mensuelles (hors crédits)",
    min_value=0.0, step=50.0,
    help="Vos charges fixes : alimentation, assurances, abonnements, factures, etc. ⚠️ N'incluez pas vos mensualités de prêts ici."
)

credits = st.number_input(
    "Mensualités autres crédits (hors immobilier)",
    min_value=0.0, step=50.0,
    help="Mensualités de crédits consommation, auto, etc. ⚠️ N'incluez pas les prêts immobiliers ici, ils seront traités séparément."
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

# --- Premier bien existant ---
st.header("1.bis. Premier bien immobilier (optionnel)")
st.markdown("Si vous avez déjà un bien immobilier avec un prêt en cours :")

a_premier_bien = st.checkbox("J'ai déjà un bien immobilier avec un prêt en cours")

premier_bien = None
if a_premier_bien:
    prix_premier = st.number_input(
        "Prix d'achat du premier bien (€)",
        min_value=0.0, step=1000.0,
        help="Prix d'achat de votre premier bien immobilier."
    )

    mensualite_premier = st.number_input(
        "Mensualité actuelle du prêt (€)",
        min_value=0.0, step=50.0,
        help="Mensualité que vous payez actuellement pour ce bien."
    )

    loyer_premier = st.number_input(
        "Loyer perçu (€)",
        min_value=0.0, step=50.0,
        help="Loyer mensuel perçu si c'est un investissement locatif. Saisir 0 si c'est votre résidence principale."
    )

    if prix_premier > 0 and mensualite_premier > 0:
        premier_bien = PremierBien(
            prix_achat=prix_premier,
            mensualite_actuelle=mensualite_premier,
            loyer_percu=loyer_premier
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
    help="Montant du loyer mensuel attendu (si investissement locatif). Saisir 0 si c'est une résidence principale."
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
    resultats = calcul_ratios(situation, premier_bien, projet)

    # Détail des revenus
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Revenus salaires", f"{resultats['revenus_salaires']:.0f} €")
    with col2:
        st.metric("Revenus locatifs", f"{resultats['revenus_locatifs']:.0f} €")
    with col3:
        st.metric("Revenus totaux", f"{resultats['revenus_totaux']:.0f} €")

    st.divider()

    # Détail des charges
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mensualités immobilier", f"{resultats['mensualites_immobilier']:.0f} €")
    with col2:
        st.metric("Autres crédits", f"{resultats['mensualites_autres_credits']:.0f} €")
    with col3:
        st.metric("Total mensualités", f"{resultats['mensualites_totales']:.0f} €")

    if projet:
        st.metric("💡 Mensualité du nouveau prêt", f"{resultats['mensualite_nouveau']:.0f} €")

    st.divider()

    # Taux et ratios
    col1, col2, col3 = st.columns(3)

    with col1:
        taux_endettement_pct = resultats['taux_endettement'] * 100
        st.metric(
            "📊 Taux d'endettement", 
            f"{taux_endettement_pct:.1f} %",
            help="Total mensualités ÷ revenus totaux (salaires + loyers). Seuil bancaire : 35%"
        )
        if taux_endettement_pct > 35:
            st.error("⚠️ Dépasse 35%")
        else:
            st.success("✅ OK")

    with col2:
        taux_effort_pct = resultats['taux_effort'] * 100
        st.metric(
            "💪 Taux d'effort", 
            f"{taux_effort_pct:.1f} %",
            help="Total mensualités ÷ revenus salaires uniquement. Indicateur de l'effort sur vos revenus professionnels."
        )
        if taux_effort_pct > 45:
            st.error("⚠️ Effort élevé")
        elif taux_effort_pct > 35:
            st.warning("⚠️ Effort modéré")
        else:
            st.success("✅ Effort faible")

    with col3:
        reste_a_vivre = resultats['reste_a_vivre']
        reste_min = 800 * situation.personnes_foyer
        st.metric(
            "💰 Reste à vivre", 
            f"{reste_a_vivre:.0f} €",
            help=f"Revenus totaux - mensualités - charges. Minimum recommandé : {reste_min}€"
        )
        if reste_a_vivre >= reste_min:
            st.success("✅ Suffisant")
        else:
            st.error("⚠️ Insuffisant")

    st.divider()

    # Verdict global
    if (resultats['taux_endettement'] <= 0.35 and 
        resultats['reste_a_vivre'] >= reste_min):
        st.success(
            "🎉 **PROJET FINANÇABLE** ✅\n\n"
            "Votre taux d'endettement et reste à vivre respectent les règles bancaires habituelles.\n"
            "➡️ Vous pouvez présenter ce projet à votre banque pour validation."
        )
    else:
        messages_problemes = []
        if resultats['taux_endettement'] > 0.35:
            messages_problemes.append(f"• Taux d'endettement trop élevé : {resultats['taux_endettement']*100:.1f}% (max 35%)")
        if resultats['reste_a_vivre'] < reste_min:
            messages_problemes.append(f"• Reste à vivre insuffisant : {reste_a_vivre:.0f}€ (min {reste_min}€)")

        st.error(
            "⚠️ **RISQUE DE REFUS BANCAIRE**\n\n" + 
            "\n".join(messages_problemes) + 
            "\n\n➡️ **Solutions possibles :**\n"
            "• Augmenter l'apport personnel\n"
            "• Allonger la durée du prêt\n"
            "• Diminuer le prix du bien\n"
            "• Optimiser les loyers attendus"
        )