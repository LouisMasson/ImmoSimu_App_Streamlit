
# 📊 Simulateur Immobilier - Analyse de Finançabilité

Une application Streamlit complète pour simuler et analyser la faisabilité de projets d'investissement immobilier.

## 🚀 Fonctionnalités

- **Simulation de financement** : Calcul automatique des ratios bancaires (taux d'endettement, reste à vivre)
- **Support multi-porteurs** : Gestion des projets à plusieurs (couples, associés)
- **Dashboard de rentabilité** : Projections sur 10 ans pour les investissements locatifs
- **Analyse IA** : Conseils personnalisés via GPT-4o
- **Export PDF** : Génération de rapports professionnels
- **Interface intuitive** : Guide pas-à-pas avec tutoriel intégré

## 📋 Prérequis

- Python 3.11+
- Clé API OpenAI (pour l'analyse IA)
- Navigateur web moderne

## 🛠️ Installation

### Sur Replit (Recommandé)

1. **Forkez ce Repl** ou créez un nouveau Repl Python
2. **Copiez les fichiers** du projet dans votre Repl
3. **Configurez les secrets** :
   - Allez dans l'onglet "Secrets" (🔒)
   - Ajoutez `OPENAI_API_KEY` avec votre clé API OpenAI
4. **Lancez l'application** avec le bouton "Run"

### Installation locale

```bash
# Cloner le projet
git clone <url-du-repo>
cd simulateur-immobilier

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé OpenAI

# Lancer l'application
streamlit run app.py
```

## 🎯 Guide d'utilisation

### 1. Configuration initiale

**Variables d'environnement requises :**
- `OPENAI_API_KEY` : Votre clé API OpenAI pour l'analyse IA

### 2. Utilisation de l'application

#### Étape 1 : Situation actuelle
- **Mode simple** : Saisie rapide pour un utilisateur unique
- **Mode multi-porteurs** : Détail par personne pour les projets à plusieurs

Renseignez :
- Revenus nets mensuels (salaires uniquement)
- Charges mensuelles fixes
- Crédits en cours (hors immobilier)
- Nombre de personnes dans le foyer

#### Étape 2 : Premier bien (optionnel)
Si vous possédez déjà un bien immobilier :
- Prix d'achat
- Mensualité actuelle
- Loyer perçu (si investissement locatif)
- Date d'achat et durée du prêt

#### Étape 3 : Nouveau projet
- Prix du bien ciblé
- Apport personnel disponible
- Taux d'intérêt proposé
- Durée du prêt souhaité
- Loyer attendu (si investissement locatif)

#### Étape 4 : Résultats et analyse
- **Ratios financiers** : Taux d'endettement, effort, reste à vivre
- **Dashboard de rentabilité** : Pour les investissements locatifs uniquement
- **Analyse IA** : Conseils personnalisés et recommandations
- **Export PDF** : Rapport complet pour votre banquier

### 3. Interprétation des résultats

#### Indicateurs clés
- **Taux d'endettement** : ≤ 35% (seuil bancaire standard)
- **Reste à vivre** : ≥ 800€/personne (minimum recommandé)
- **Taux d'effort** : Impact sur les revenus salariaux uniquement

#### Codes couleur
- 🟢 **Vert** : Conforme aux critères bancaires
- 🟡 **Orange** : Zone de vigilance
- 🔴 **Rouge** : Risque de refus bancaire

## 📊 Dashboard de rentabilité

**Disponible uniquement pour les investissements locatifs** (loyer attendu > 0)

### Métriques calculées
- **Cash-flow** : Flux de trésorerie nets annuels et cumulés
- **Rendements** : Brut et net, évolution dans le temps
- **Patrimoine** : Construction du patrimoine net sur 10 ans
- **ROI** : Retour sur investissement total

### Hypothèses de calcul
- Inflation des loyers : +2% par an
- Valorisation du bien : +2% par an
- Charges propriétaire : 0,3% de la valeur/mois
- Inflation des charges : +2,5% par an

## 🤖 Analyse IA

L'analyse IA utilise GPT-4o comme conseiller patrimonial virtuel.

### Fonctionnalités
- Analyse personnalisée de votre situation
- Identification des points forts et risques
- Recommandations d'optimisation
- Conseils adaptés à votre profil

### Coût
- Environ 0,01-0,03€ par analyse
- Facturé sur votre compte OpenAI

## 📄 Export PDF

Génère un rapport professionnel incluant :
- Synthèse de votre situation
- Détail des calculs
- Graphiques de rentabilité
- Analyse IA (si effectuée)
- Recommandations

## ⚠️ Limitations et avertissements

### Importantes limitations
- **Simulation indicative** : Ne remplace pas l'analyse de votre banquier
- **Hypothèses simplifiées** : Les projections sont basées sur des moyennes
- **Pas de conseil en investissement** : L'outil est informatif uniquement

### Données non traitées
- Fiscalité (IFI, impôts fonciers, etc.)
- Frais de notaire et d'agence
- Travaux et rénovations
- Vacance locative
- Évolution des taux d'intérêt

## 🔧 Configuration avancée

### Variables d'environnement optionnelles

```env
# Configuration Streamlit
STREAMLIT_SERVER_PORT=5000
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Configuration OpenAI
OPENAI_TIMEOUT=30
OPENAI_MAX_TOKENS=150
```

### Personnalisation

Les hypothèses de calcul peuvent être modifiées dans `dashboard_rentabilite.py` :

```python
# Paramètres modifiables
INFLATION_LOYERS = 0.02      # 2% par an
VALORISATION_BIEN = 0.02     # 2% par an
CHARGES_PROPRIETAIRE = 0.003 # 0,3% par mois
INFLATION_CHARGES = 0.025    # 2,5% par an
```

## 🚀 Déploiement en production

### Sur Replit Deployments

1. **Configurez les secrets** dans l'onglet Deployments
2. **Vérifiez la commande de démarrage** :
   ```
   streamlit run --server.address 0.0.0.0 --server.headless true --server.enableCORS=false --server.enableWebsocketCompression=false app.py
   ```
3. **Déployez** avec le bouton "Deploy"

### Sécurité en production

- ✅ Clé API OpenAI sécurisée via variables d'environnement
- ✅ Validation des entrées utilisateur
- ✅ Timeout sur les appels API
- ✅ Gestion d'erreurs robuste
- ✅ Pas de stockage de données sensibles

## 🐛 Dépannage

### Problèmes courants

**Erreur "Clé API OpenAI non configurée"**
- Vérifiez que `OPENAI_API_KEY` est défini dans les Secrets
- La clé doit commencer par `sk-`

**L'analyse IA ne fonctionne pas**
- Vérifiez votre crédit OpenAI
- Testez votre clé API sur platform.openai.com

**Export PDF échoue**
- Vérifiez que tous les champs obligatoires sont remplis
- Relancez le calcul avant l'export

**Dashboard de rentabilité manquant**
- Le loyer attendu doit être > 0
- Seuls les investissements locatifs affichent ce dashboard

### Support

Pour obtenir de l'aide :
1. Consultez cette documentation
2. Vérifiez les logs dans l'onglet Console
3. Visitez le [Community Hub Replit](https://replit.com/community)

## 📚 Structure du projet

```
├── app.py                    # Application principale Streamlit
├── data_models.py           # Modèles de données Pydantic
├── calculs.py              # Logique de calcul des ratios
├── dashboard_rentabilite.py # Dashboard et projections
├── analyse_ia.py           # Intégration OpenAI GPT-4o
├── export_pdf.py           # Génération de rapports PDF
├── requirements.txt        # Dépendances Python
├── .env.example           # Template variables d'environnement
├── .streamlit/            # Configuration Streamlit
└── README.md             # Cette documentation
```

## 📈 Évolutions futures

- [ ] Intégration de données de marché en temps réel
- [ ] Calculs fiscaux avancés
- [ ] Simulation de plusieurs scénarios
- [ ] API REST pour intégration externe
- [ ] Historique des simulations

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**⚠️ Disclaimer** : Cet outil est fourni à titre informatif uniquement. Il ne constitue pas un conseil en investissement ou une garantie de financement. Consultez toujours un professionnel qualifié pour vos décisions financières.
