
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional
from data_models import SituationActuelle, NouveauProjet, PremierBien

def calculer_projection_rentabilite(situation: SituationActuelle, premier_bien: Optional[PremierBien], projet: Optional[NouveauProjet], resultats: dict, annees: int = 10):
    """
    Calcule les projections de rentabilité sur plusieurs années.
    """
    if not projet:
        return None
    
    # Données de base
    capital_emprunte = projet.prix_bien - projet.apport
    mensualite = resultats.get('mensualite_nouveau', 0)
    loyer_mensuel = projet.loyer_attendu
    
    # Paramètres d'évolution (hypothèses)
    inflation_loyers = 0.02  # 2% par an
    inflation_charges = 0.025  # 2,5% par an
    charges_mensuelles_initiales = projet.prix_bien * 0.003  # 0,3% du prix par mois (charges propriétaire)
    
    # Calcul année par année
    donnees_projection = []
    
    for annee in range(1, annees + 1):
        # Évolution des loyers
        loyer_annuel = loyer_mensuel * 12 * (1 + inflation_loyers) ** (annee - 1)
        
        # Évolution des charges
        charges_annuelles = charges_mensuelles_initiales * 12 * (1 + inflation_charges) ** (annee - 1)
        
        # Amortissement du capital (approximation linéaire pour simplifier)
        capital_rembourse = (mensualite * 12 * annee) - (capital_emprunte * (projet.taux_nominal / 100) * annee)
        capital_restant = max(0, capital_emprunte - capital_rembourse)
        
        # Cash-flow net annuel
        cash_flow_net = loyer_annuel - (mensualite * 12) - charges_annuelles
        
        # Cash-flow cumulé
        if annee == 1:
            cash_flow_cumule = cash_flow_net - projet.apport  # Inclure l'apport initial
        else:
            cash_flow_cumule = donnees_projection[-1]['cash_flow_cumule'] + cash_flow_net
        
        # Rendement locatif brut
        rendement_brut = (loyer_annuel / projet.prix_bien) * 100 if projet.prix_bien > 0 else 0
        
        # Rendement net (après charges et intérêts)
        rendement_net = (cash_flow_net / projet.apport) * 100 if projet.apport > 0 else 0
        
        # Plus-value théorique (hypothèse +2% par an)
        valorisation_bien = projet.prix_bien * (1.02 ** annee)
        plus_value_latente = valorisation_bien - projet.prix_bien
        
        # Patrimoine net (valeur bien - capital restant)
        patrimoine_net = valorisation_bien - capital_restant
        
        donnees_projection.append({
            'annee': annee,
            'loyer_annuel': loyer_annuel,
            'charges_annuelles': charges_annuelles,
            'cash_flow_net': cash_flow_net,
            'cash_flow_cumule': cash_flow_cumule,
            'capital_rembourse': capital_emprunte - capital_restant,
            'capital_restant': capital_restant,
            'rendement_brut': rendement_brut,
            'rendement_net': rendement_net,
            'valorisation_bien': valorisation_bien,
            'plus_value_latente': plus_value_latente,
            'patrimoine_net': patrimoine_net,
            'roi_total': ((cash_flow_cumule + plus_value_latente) / projet.apport) * 100 if projet.apport > 0 else 0
        })
    
    return pd.DataFrame(donnees_projection)

def afficher_dashboard_rentabilite(situation: SituationActuelle, premier_bien: Optional[PremierBien], projet: Optional[NouveauProjet], resultats: dict):
    """
    Affiche le dashboard de rentabilité avec graphiques interactifs.
    """
    st.header("📈 Dashboard de Rentabilité - Projection 10 ans")
    
    if not projet:
        st.warning("⚠️ Aucun projet défini. Veuillez d'abord renseigner un projet immobilier.")
        return
    
    if projet.loyer_attendu <= 0:
        st.warning("⚠️ Ce dashboard est conçu pour les investissements locatifs. Veuillez renseigner un loyer attendu.")
        return
    
    # Calcul des projections
    df_projection = calculer_projection_rentabilite(situation, premier_bien, projet, resultats)
    
    if df_projection is None:
        st.error("❌ Erreur lors du calcul des projections.")
        return
    
    # Métriques clés sur 10 ans
    st.subheader("🎯 Indicateurs clés à 10 ans")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        cash_flow_10ans = df_projection.iloc[-1]['cash_flow_cumule']
        st.metric(
            "Cash-flow cumulé", 
            f"{cash_flow_10ans:,.0f} €",
            help="Total des flux de trésorerie générés sur 10 ans (net de l'apport initial)"
        )
    
    with col2:
        patrimoine_10ans = df_projection.iloc[-1]['patrimoine_net']
        st.metric(
            "Patrimoine net", 
            f"{patrimoine_10ans:,.0f} €",
            help="Valeur du bien moins le capital restant dû"
        )
    
    with col3:
        roi_total_10ans = df_projection.iloc[-1]['roi_total']
        st.metric(
            "ROI total", 
            f"{roi_total_10ans:.1f}%",
            help="Retour sur investissement total (cash-flow + plus-value) / apport initial"
        )
    
    with col4:
        capital_rembourse_10ans = df_projection.iloc[-1]['capital_rembourse']
        pct_rembourse = (capital_rembourse_10ans / (projet.prix_bien - projet.apport)) * 100
        st.metric(
            "Capital remboursé", 
            f"{pct_rembourse:.1f}%",
            help="Pourcentage du prêt remboursé après 10 ans"
        )
    
    st.divider()
    
    # Graphique de construction du patrimoine
    st.subheader("🏠 Construction du Patrimoine")
    
    fig_patrimoine = go.Figure()
    
    fig_patrimoine.add_trace(
        go.Scatter(
            x=df_projection['annee'],
            y=df_projection['valorisation_bien'],
            mode='lines+markers',
            name='Valeur du bien',
            line=dict(color='green', width=3),
            fill='tonexty'
        )
    )
    
    fig_patrimoine.add_trace(
        go.Scatter(
            x=df_projection['annee'],
            y=df_projection['capital_restant'],
            mode='lines+markers',
            name='Capital restant dû',
            line=dict(color='red', width=2),
            fill='tozeroy'
        )
    )
    
    fig_patrimoine.add_trace(
        go.Scatter(
            x=df_projection['annee'],
            y=df_projection['patrimoine_net'],
            mode='lines+markers',
            name='Patrimoine net',
            line=dict(color='gold', width=3)
        )
    )
    
    fig_patrimoine.update_layout(
        title="Construction du Patrimoine Immobilier",
        xaxis_title="Année",
        yaxis_title="Valeur (€)",
        height=500
    )
    
    st.plotly_chart(fig_patrimoine, use_container_width=True)
    
    # 4. Tableau de synthèse par année
    st.subheader("📋 Tableau de Synthèse Détaillé")
    
    # Préparer le tableau pour l'affichage
    df_display = df_projection.copy()
    df_display = df_display.round(0).astype(int)
    
    # Formater les colonnes pour l'affichage
    columns_to_show = {
        'annee': 'Année',
        'loyer_annuel': 'Loyers (€)',
        'cash_flow_net': 'Cash-flow net (€)',
        'cash_flow_cumule': 'Cash-flow cumulé (€)',
        'rendement_net': 'Rendement net (%)',
        'patrimoine_net': 'Patrimoine net (€)',
        'roi_total': 'ROI total (%)'
    }
    
    df_formatted = df_display[list(columns_to_show.keys())].rename(columns=columns_to_show)
    
    # Appliquer un style conditionnel
    st.dataframe(
        df_formatted,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cash-flow cumulé (€)": st.column_config.NumberColumn(
                format="€%d",
                help="Cash-flow cumulé depuis le début"
            ),
            "ROI total (%)": st.column_config.NumberColumn(
                format="%.1f%%",
                help="Retour sur investissement total"
            ),
            "Rendement net (%)": st.column_config.NumberColumn(
                format="%.1f%%",
                help="Rendement net annuel"
            )
        }
    )
    
    # Hypothèses utilisées
    st.subheader("📝 Hypothèses de Calcul")
    
    with st.expander("Voir les hypothèses utilisées pour les projections"):
        st.markdown("""
        **Hypothèses de calcul utilisées :**
        
        - 📈 **Inflation des loyers** : +2% par an
        - 🏠 **Valorisation du bien** : +2% par an  
        - 💸 **Charges propriétaire** : 0,3% de la valeur du bien par mois
        - 📊 **Inflation des charges** : +2,5% par an
        - 💰 **Amortissement** : Calculé de manière simplifiée
        
        ⚠️ **Attention** : Ces projections sont indicatives et basées sur des hypothèses moyennes. 
        Les performances réelles peuvent varier selon les conditions de marché, la localisation, 
        l'état du bien, etc.
        """)
    
    # Analyse rapide
    st.subheader("🎯 Analyse Rapide")
    
    # Point de rentabilité
    break_even_year = None
    for idx, row in df_projection.iterrows():
        if row['cash_flow_cumule'] > 0:
            break_even_year = row['annee']
            break
    
    col1, col2 = st.columns(2)
    
    with col1:
        if break_even_year:
            st.success(f"✅ **Rentabilité atteinte** : Année {break_even_year}")
        else:
            st.warning("⚠️ **Rentabilité non atteinte** sur 10 ans")
        
        rendement_moyen = df_projection['rendement_net'].mean()
        if rendement_moyen > 5:
            st.success(f"✅ **Rendement attractif** : {rendement_moyen:.1f}% en moyenne")
        elif rendement_moyen > 2:
            st.info(f"ℹ️ **Rendement correct** : {rendement_moyen:.1f}% en moyenne")
        else:
            st.warning(f"⚠️ **Rendement faible** : {rendement_moyen:.1f}% en moyenne")
    
    with col2:
        roi_final = df_projection.iloc[-1]['roi_total']
        if roi_final > 100:
            st.success(f"🚀 **ROI excellent** : {roi_final:.1f}% sur 10 ans")
        elif roi_final > 50:
            st.success(f"✅ **ROI satisfaisant** : {roi_final:.1f}% sur 10 ans")
        elif roi_final > 0:
            st.info(f"ℹ️ **ROI positif** : {roi_final:.1f}% sur 10 ans")
        else:
            st.error(f"❌ **ROI négatif** : {roi_final:.1f}% sur 10 ans")
