from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generer_pdf_simulation(resultats, situation, premier_bien=None, projet=None, analyse_ia=None):
    """Génère un PDF avec les résultats de la simulation."""

    # Créer un buffer en mémoire
    buffer = BytesIO()

    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )

    # Contenu du PDF
    elements = []

    # Titre
    elements.append(Paragraph("📊 Rapport de Simulation Immobilière", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Situation financière
    elements.append(Paragraph("💰 Situation Financière", heading_style))

    data_situation = [
        ['Revenus salaires mensuels', f"{resultats['revenus_salaires']:.0f} €"],
        ['Revenus locatifs mensuels', f"{resultats['revenus_locatifs']:.0f} €"],
        ['Revenus totaux mensuels', f"{resultats['revenus_totaux']:.0f} €"],
        ['Mensualités autres crédits', f"{resultats['mensualites_autres_credits']:.0f} €"],
    ]

    if premier_bien:
        data_situation.append(['Mensualité premier bien', f"{resultats['mensualite_premier_bien']:.0f} €"])
        # Ajouter la date du premier achat et l'ancienneté du prêt si disponibles dans les résultats
        if 'date_premier_achat' in resultats and resultats['date_premier_achat']:
            data_situation.append(['Date du premier achat', datetime.fromtimestamp(resultats['date_premier_achat']).strftime('%d/%m/%Y')])
        if 'anciennete_pret_annees' in resultats and resultats['anciennete_pret_annees'] is not None:
            data_situation.append(['Ancienneté du prêt', f"{resultats['anciennete_pret_annees']:.1f} ans"])


    if projet:
        data_situation.append(['Mensualité nouveau projet', f"{resultats['mensualite_nouveau']:.0f} €"])

    data_situation.append(['Total mensualités', f"{resultats['mensualites_totales']:.0f} €"])

    table_situation = Table(data_situation, colWidths=[8*cm, 4*cm])
    table_situation.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table_situation)
    elements.append(Spacer(1, 20))

    # Indicateurs clés
    elements.append(Paragraph("📊 Indicateurs Clés", heading_style))

    taux_endettement_pct = resultats['taux_endettement'] * 100
    taux_effort_pct = resultats['taux_effort'] * 100
    reste_a_vivre = resultats['reste_a_vivre']
    reste_min = 800 * situation.personnes_foyer

    # Déterminer les statuts
    statut_endettement = "✅ CONFORME" if taux_endettement_pct <= 35 else "⚠️ DÉPASSÉ"
    statut_effort = "✅ FAIBLE" if taux_effort_pct <= 35 else ("⚠️ MODÉRÉ" if taux_effort_pct <= 45 else "❌ ÉLEVÉ")
    statut_reste = "✅ SUFFISANT" if reste_a_vivre >= reste_min else "❌ INSUFFISANT"

    data_ratios = [
        ['Indicateur', 'Valeur', 'Seuil', 'Statut'],
        ['Taux d\'endettement', f"{taux_endettement_pct:.1f}%", "≤ 35%", statut_endettement],
        ['Taux d\'effort', f"{taux_effort_pct:.1f}%", "≤ 35%", statut_effort],
        ['Reste à vivre', f"{reste_a_vivre:.0f} €", f"≥ {reste_min} €", statut_reste],
    ]

    table_ratios = Table(data_ratios, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
    table_ratios.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table_ratios)
    elements.append(Spacer(1, 20))

    # Détail du projet si applicable
    if projet:
        elements.append(Paragraph("🏠 Détail du Nouveau Projet", heading_style))

        capital_emprunte = projet.prix_bien - projet.apport

        data_projet = [
            ['Prix du bien', f"{projet.prix_bien:.0f} €"],
            ['Apport personnel', f"{projet.apport:.0f} €"],
            ['Capital emprunté', f"{capital_emprunte:.0f} €"],
            ['Taux nominal', f"{projet.taux_nominal:.2f}%"],
            ['Durée du prêt', f"{projet.duree_annees} ans"],
            ['Mensualité calculée', f"{resultats['mensualite_nouveau']:.0f} €"],
        ]

        if projet.loyer_attendu > 0:
            data_projet.append(['Loyer attendu', f"{projet.loyer_attendu:.0f} €"])

        table_projet = Table(data_projet, colWidths=[8*cm, 4*cm])
        table_projet.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table_projet)
        elements.append(Spacer(1, 20))

    # Détail par porteur si applicable
    if resultats.get('details_porteurs'):
        elements.append(Paragraph("👥 Détail par Porteur du Projet", heading_style))

        for detail in resultats['details_porteurs']:
            elements.append(Paragraph(f"• {detail['nom']} - {detail['pourcentage']}% du projet", styles['Normal']))

            data_porteur = [
                ['Revenus salaires', f"{detail['revenus_salaires']:.0f} €"],
                ['Revenus locatifs', f"{detail['revenus_locatifs']:.0f} €"],
                ['Revenus totaux', f"{detail['revenus_totaux']:.0f} €"],
                ['Mensualités totales', f"{detail['mensualites_totales']:.0f} €"],
                ['Taux d\'endettement', f"{detail['taux_endettement']*100:.1f}%"],
                ['Taux d\'effort', f"{detail['taux_effort']*100:.1f}%"],
                ['Reste à vivre', f"{detail['reste_a_vivre']:.0f} €"],
            ]

            table_porteur = Table(data_porteur, colWidths=[8*cm, 4*cm])
            table_porteur.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightyellow),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table_porteur)
            elements.append(Spacer(1, 10))

    # Analyse IA si disponible
    if analyse_ia:
        elements.append(Paragraph("🤖 Analyse du Conseiller IA", heading_style))

        # Nettoyer le texte de l'analyse pour le PDF
        analyse_text = analyse_ia.replace('**', '').replace('*', '').replace('#', '')

        # Diviser l'analyse en paragraphes
        paragraphes = analyse_text.split('\n\n')
        for paragraphe in paragraphes:
            if paragraphe.strip():
                elements.append(Paragraph(paragraphe.strip(), styles['Normal']))
                elements.append(Spacer(1, 6))

        elements.append(Spacer(1, 20))

    # Verdict final
    elements.append(Paragraph("🎯 Verdict Final", heading_style))

    if (resultats['taux_endettement'] <= 0.35 and 
        resultats['reste_a_vivre'] >= reste_min):
        verdict_text = "✅ PROJET FINANÇABLE - Votre projet respecte les critères bancaires habituels."
        verdict_color = colors.darkgreen
    else:
        verdict_text = "⚠️ RISQUE DE REFUS BANCAIRE - Votre projet dépasse les seuils recommandés."
        verdict_color = colors.darkred

    verdict_style = ParagraphStyle(
        'Verdict',
        parent=styles['Normal'],
        fontSize=12,
        textColor=verdict_color,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph(verdict_text, verdict_style))
    elements.append(Spacer(1, 20))

    # Note de bas de page
    elements.append(Paragraph(
        "⚠️ Cette simulation est indicative et ne constitue pas un engagement de financement. "
        "Consultez votre conseiller bancaire pour une étude personnalisée.",
        styles['Italic']
    ))

    # Construire le PDF
    doc.build(elements)

    # Retourner le buffer
    buffer.seek(0)
    return buffer