import streamlit as st
from data_models import SituationActuelle, NouveauProjet, PremierBien, PorteurProjet
from calculs import calcul_ratios
from export_pdf import generer_pdf_simulation
from analyse_ia import analyser_projet_avec_ia

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

mode_porteurs = st.radio(
    "Mode de saisie :",
    ["Saisie simple", "Projet à plusieurs (couple, associés...)"],
    help="Choisissez 'Projet à plusieurs' si vous voulez détailler les revenus/charges de chaque porteur du projet."
)

porteurs = []
if mode_porteurs == "Projet à plusieurs":
    st.subheader("👥 Porteurs du projet")
    
    nb_porteurs = st.number_input(
        "Nombre de porteurs du projet",
        min_value=2, max_value=4, value=2, step=1,
        help="Nombre de personnes qui participent financièrement au projet (ex: 2 pour un couple)."
    )
    
    total_pourcentage = 0
    for i in range(nb_porteurs):
        st.write(f"**Porteur {i+1} :**")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input(f"Nom/Prénom", value=f"Porteur {i+1}", key=f"nom_{i}")
            revenus_porteur = st.number_input(
                f"Revenus nets mensuels (€)", 
                min_value=0.0, step=100.0, key=f"revenus_{i}",
                help="Salaires nets de cette personne."
            )
            charges_porteur = st.number_input(
                f"Charges mensuelles (€)", 
                min_value=0.0, step=50.0, key=f"charges_{i}",
                help="Charges fixes personnelles de cette personne."
            )
        
        with col2:
            credits_porteur = st.number_input(
                f"Crédits mensuels (€)", 
                min_value=0.0, step=50.0, key=f"credits_{i}",
                help="Mensualités crédits personnels de cette personne."
            )
            pourcentage = st.number_input(
                f"% de participation au projet", 
                min_value=0.0, max_value=100.0, step=5.0, key=f"pourcentage_{i}",
                help="Pourcentage de participation de cette personne dans le projet immobilier."
            )
        
        total_pourcentage += pourcentage
        
        if revenus_porteur > 0 and pourcentage > 0:
            porteurs.append(PorteurProjet(
                nom=nom,
                revenus_mensuels=revenus_porteur,
                charges_mensuelles=charges_porteur,
                credits_mensuels=credits_porteur,
                pourcentage_projet=pourcentage
            ))
    
    if abs(total_pourcentage - 100) > 0.1:
        st.error(f"⚠️ La somme des pourcentages doit être 100%. Actuellement : {total_pourcentage}%")
    else:
        st.success(f"✅ Répartition OK : {total_pourcentage}%")

    personnes = st.number_input(
        "Nombre de personnes dans le foyer",
        min_value=1, step=1,
        help="Nombre total de personnes vivant dans le foyer (adulte(s) + enfants)."
    )

    situation = SituationActuelle(
        revenus_mensuels=0,  # Sera calculé à partir des porteurs
        charges_mensuelles=0,  # Sera calculé à partir des porteurs
        credits_mensuels=0,  # Sera calculé à partir des porteurs
        personnes_foyer=personnes,
        porteurs=porteurs,
    )

else:
    # Mode simple
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

    # Détails par porteur si applicable
    if resultats.get('details_porteurs'):
        st.divider()
        st.subheader("📊 Détail par porteur du projet")
        
        for detail in resultats['details_porteurs']:
            with st.expander(f"👤 {detail['nom']} - {detail['pourcentage']}% du projet"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Revenus salaires", f"{detail['revenus_salaires']:.0f} €")
                    st.metric("Revenus locatifs", f"{detail['revenus_locatifs']:.0f} €")
                    st.metric("Revenus totaux", f"{detail['revenus_totaux']:.0f} €")
                
                with col2:
                    st.metric("Mensualités totales", f"{detail['mensualites_totales']:.0f} €")
                    
                    taux_end_pct = detail['taux_endettement'] * 100
                    st.metric("Taux d'endettement", f"{taux_end_pct:.1f} %")
                    if taux_end_pct > 35:
                        st.error("⚠️ > 35%")
                    else:
                        st.success("✅ OK")
                
                with col3:
                    taux_eff_pct = detail['taux_effort'] * 100
                    st.metric("Taux d'effort", f"{taux_eff_pct:.1f} %")
                    
                    st.metric("Reste à vivre", f"{detail['reste_a_vivre']:.0f} €")
                    if detail['reste_a_vivre'] >= 800:
                        st.success("✅ OK")
                    else:
                        st.error("⚠️ Faible")

    st.divider()

    # Analyse IA
    st.header("🤖 Analyse IA - Conseiller Patrimonial")
    st.markdown("""
    Obtenez une analyse personnalisée de votre projet par notre IA spécialisée en conseil patrimonial.
    L'IA analysera vos indicateurs financiers et vous donnera des recommandations adaptées à votre situation.
    """)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🔍 Analyser mon projet avec l'IA", type="secondary", use_container_width=True):
            with st.spinner("🤖 Analyse en cours par notre conseiller IA..."):
                analyse = analyser_projet_avec_ia(resultats, situation, premier_bien, projet)
                # Sauvegarder l'analyse en session pour l'export PDF
                st.session_state['derniere_analyse_ia'] = analyse
            
            st.markdown("### 📋 Analyse et Recommandations")
            
            # Afficher l'analyse dans un container stylé
            with st.container():
                st.markdown(f"""
                <div style="
                    background-color: #f8f9fa;
                    border-left: 5px solid #007bff;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                ">
                {analyse.replace('\n', '<br>')}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.info("""
        💡 **À propos de l'analyse IA**
        
        Notre IA utilise GPT-4o et agit comme un conseiller patrimonial expérimenté.
        
        ⚠️ Cette analyse est à titre informatif et ne remplace pas l'avis d'un professionnel.
        """)

    st.divider()

    # Bouton d'export PDF
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📄 Télécharger le rapport PDF", type="primary", use_container_width=True):
            try:
                # Récupérer l'analyse IA si elle existe dans la session
                analyse_ia = st.session_state.get('derniere_analyse_ia', None)
                pdf_buffer = generer_pdf_simulation(resultats, situation, premier_bien, projet, analyse_ia)
                
                # Créer le nom du fichier avec la date
                from datetime import datetime
                nom_fichier = f"simulation_immobiliere_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                
                st.download_button(
                    label="💾 Cliquez ici pour télécharger",
                    data=pdf_buffer.getvalue(),
                    file_name=nom_fichier,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success("✅ PDF généré avec succès ! Cliquez sur le bouton ci-dessus pour télécharger.")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération du PDF : {str(e)}")

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