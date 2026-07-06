# Scripts importants du projet Estate AI

## Objectif

Ce document sert de support de presentation technique. Il explique les scripts les plus importants du projet, leur role, leurs entrees/sorties, les commandes utiles et les competences RNCP qu'ils permettent de soutenir.

Le projet couvre principalement :

- E1 : collecte, stockage et mise a disposition des donnees.
- E3 : exposition, integration, tests et monitorage du modele IA.
- E4 : application, integration continue, livraison et exploitation.

## Vue d'ensemble des flux

Le fonctionnement global suit cette chaine :

1. Les donnees sources sont lues depuis `data/train.csv` et `data/test.csv`.
2. Les scripts ETL nettoient, normalisent et exportent les donnees.
3. Les donnees nettoyees sont chargees dans PostgreSQL/Neon.
4. Le modele XGBoost est entraine et sauvegarde en artefact `.joblib`.
5. FastAPI expose les donnees, les predictions, les metriques et l'assistant.
6. React consomme l'API pour afficher les dashboards, la prediction et l'historique.
7. Les tests et GitHub Actions verifient automatiquement le fonctionnement.

## Scripts de configuration et demarrage

### `main.py`

Role :

- Point d'entree simple du projet.
- Permet de lancer l'application principale sans memoriser le chemin interne FastAPI.

Interet soutenance :

- Montre qu'il existe un point d'acces clair au service applicatif.

Competences :

- C9 : exposition du modele via API.
- C17 : application executable.

### `backend/app/main.py`

Role :

- Cree l'application FastAPI.
- Configure CORS.
- Inclut le routeur API.
- Initialise la base si elle est accessible.
- Sert le frontend compile si `frontend/dist` existe.

Points importants :

- `app = FastAPI(title="Real Estate AI Platform", version="1.0.0")`
- `app.include_router(router)`
- `StaticFiles` permet de servir l'application React en production.

Commande utile :

```bash
python -m uvicorn backend.app.main:app --reload
```

Competences :

- C9 : API REST du modele.
- C10 : integration API/application.
- C17 : composants techniques applicatifs.

### `backend/config/settings.py`

Role :

- Centralise les variables d'environnement.
- Utilise `pydantic-settings` pour charger et typer la configuration.

Variables importantes :

- `DATABASE_URL`
- `MODEL_PATH`
- `MODEL_VERSION`
- `API_KEY`
- `OPENROUTER_API_KEY`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USE_TLS`

Interet soutenance :

- Montre l'externalisation de la configuration.
- Evite les secrets en dur dans le code.
- Facilite le deploiement Render/Neon.

Competences :

- C8 : parametrage d'un service.
- C9 : configuration API/modele.
- C13/C19 : reproductibilite en CI/CD.
- C17 : environnement applicatif.

### `.env.example`

Role :

- Sert de modele pour configurer l'application.
- Liste les variables attendues sans exposer de secrets reels.

Interet soutenance :

- Prouve que le projet est reinstallable.
- Aide a expliquer les dependances de l'environnement.

## Scripts API et backend applicatif

### `backend/app/api.py`

Role :

- Contient les routes REST principales.
- Expose les donnees de marche.
- Expose le modele IA via `/api/predict`.
- Expose les metriques du modele.
- Expose l'historique des predictions.
- Expose l'assistant IA.

Routes importantes :

- `GET /api/health`
- `GET /api/market-dashboard`
- `GET /api/filters`
- `GET /api/overview`
- `GET /api/market-data`
- `POST /api/predict`
- `GET /api/prediction-history`
- `GET /api/model-metrics/latest`
- `GET /api/model-metrics/history`
- `POST /api/chat`

Fonctions importantes :

- `build_filtered_query()` : applique les filtres marche.
- `build_market_summary()` : construit le contexte marche pour l'assistant.
- `validate_prediction_payload()` : controle le payload de prediction par liste `FEATURES`.
- `predict()` : charge le modele, execute l'inference, sauvegarde l'historique.
- `latest_model_metrics()` : restitue les dernieres metriques.
- `model_metrics_history()` : restitue l'historique des metriques.
- `chat()` : fournit une reponse locale ou OpenRouter selon la configuration.

Validation C9 :

- Le rapport E3 indique que la validation de prediction ne repose pas sur un schema Pydantic dedie.
- Le code reste coherent avec ce rapport : il utilise `payload: dict` et une validation explicite par `FEATURES`.
- La validation a ete renforcee sur les champs manquants, numeriques et categoriels.

Securite :

- Les routes sensibles utilisent `Security(require_api_key)`.
- `/api/predict`, `/api/prediction-history`, `/api/batch-predictions`, `/api/model-metrics/latest` et `/api/model-metrics/history` exigent `X-API-Key`.

Competences :

- C5 : API REST de mise a disposition des donnees.
- C9 : API exposant le modele IA.
- C10 : integration du modele dans l'application.
- C11 : restitution des metriques.
- C17 : composants backend.

### `backend/app/auth.py`

Role :

- Implemente l'authentification par cle API.
- Lit la cle attendue depuis `API_KEY`.
- Valide le header HTTP `X-API-Key`.
- Renvoie `401 Unauthorized` si la cle est absente ou invalide.

Fonctions importantes :

- `require_api_key()`
- `APIKeyHeader(name="X-API-Key")`

Interet soutenance :

- Montre une protection simple mais fonctionnelle des routes sensibles.
- Correspond au rapport E3 qui parle d'authentification par cle API.

Competences :

- C5 : autorisation API data.
- C9 : securisation de l'API modele.
- C17 : gestion des droits d'acces.

### `backend/app/models.py`

Role :

- Definit les modeles ORM SQLAlchemy.
- Fait le lien entre le code Python et les tables SQL.

Tables principales :

- `PropertyTrain`
- `ModelMetric`
- `BatchPrediction`
- `UserPrediction`
- `ExternalMarketContext`
- `ScrapedMarketTrend`
- `ExternalContextSummary`

Interet soutenance :

- Montre la persistance des donnees metier, predictions et metriques.

Competences :

- C4 : structure de stockage.
- C5 : donnees disponibles pour API.
- C11 : stockage des metriques.
- C17 : couche metier backend.

### `backend/app/database.py`

Role :

- Configure l'acces base de donnees pour FastAPI.
- Fournit `get_db()` aux routes.
- Gere le moteur SQLAlchemy et les sessions.

Interet soutenance :

- Montre une separation propre entre API et persistance.

Competences :

- C4 : connexion base.
- C5 : mise a disposition via API.
- C17 : architecture applicative.

### `backend/app/schemas.py`

Role :

- Definit des schemas Pydantic pour les reponses de metriques.

Schemas :

- `ModelMetricsResponse`
- `ModelMetricsHistoryResponse`

Utilisation :

- `response_model=ModelMetricsResponse`
- `response_model=ModelMetricsHistoryResponse`

Interet soutenance :

- Prouve que certains contrats d'API sont formalises avec Pydantic.
- Attention : `/api/predict` garde une validation manuelle, conformement au rapport E3.

Competences :

- C9 : contrat d'API.
- C11 : contrat de restitution des metriques.
- C12 : validation testable.

### `backend/app/analytics.py`

Role :

- Regroupe de la logique d'analyse metier si utilisee par l'application.
- Sert a isoler certains calculs analytiques du routeur API.

Interet soutenance :

- Montre une separation possible entre routes et logique d'analyse.

Competences :

- C5 : exposition de donnees analysees.
- C17 : composants metier.

## Scripts ETL et donnees

### `backend/etl/ingest_data.py`

Role :

- Lit les fichiers CSV sources.
- Resout les chemins de fichiers.
- Controle les colonnes minimales attendues.

Fonctions importantes :

- `resolve_data_path()`
- `ingest_csv()`
- `validate_train_columns()`

Validations :

- Fichier introuvable : `FileNotFoundError`.
- CSV illisible : `ValueError`.
- Colonne `SalePrice` manquante : `ValueError`.

Commande utile :

```bash
python -m backend.etl.ingest_data data/train.csv
```

Competences :

- C1 : extraction fichier.
- C3 : preparation avant nettoyage.

### `backend/etl/clean_data.py`

Role :

- Nettoie les jeux de donnees.
- Selectionne les variables utiles.
- Standardise les colonnes.
- Gere les valeurs manquantes.
- Supprime doublons et outliers.
- Cree `property_age`.
- Exporte des snapshots data lake.

Fonctions importantes :

- `standardize_columns()`
- `select_relevant_columns()`
- `add_property_age()`
- `fill_missing_values()`
- `remove_duplicates_and_outliers()`
- `clean_dataframe()`
- `enforce_row_limit()`
- `export_data_lake_snapshot()`
- `clean_and_save()`

Sorties produites :

- `data/processed/train_clean.csv`
- `data/processed/test_clean.csv`
- `data/lake/raw/train_raw.parquet.gzip`
- `data/lake/raw/test_raw.parquet.gzip`
- `data/lake/processed/train_clean.parquet.gzip`
- `data/lake/processed/test_clean.parquet.gzip`

Commande utile :

```bash
python -m backend.etl.clean_data
```

Competences :

- C1 : automatisation de traitement des donnees.
- C3 : nettoyage, normalisation, aggregation.
- C12 : donnees fiables pour tests modele.

### `backend/etl/fetch_external_context.py`

Role :

- Collecte des indicateurs externes via API FRED.
- Transforme les reponses JSON en DataFrame.
- Produit un CSV et un resume JSON.
- Peut charger les resultats en base.

Source :

- API FRED, via `FRED_API_KEY`.

Sorties :

- `data/external/external_market_context.csv`
- `data/external/external_market_summary.json`

Fonctions importantes :

- `_fetch_fred_series()`
- `_build_dataframe()`
- `_build_summary()`
- `fetch_external_context()`

Commande utile :

```bash
python -m backend.etl.fetch_external_context
```

Competences :

- C1 : extraction depuis API REST.
- C3 : transformation des donnees externes.
- C5/C10 : contexte exploitable par API et frontend.

### `backend/etl/scrape_market_trends.py`

Role :

- Scrape des tendances marche depuis HTML local ou URL.
- Peut utiliser une recherche web DuckDuckGo HTML.
- Parse des pages de type tableau ou cartes HTML.
- Sauvegarde un CSV et un resume JSON.
- Peut charger les resultats dans Neon.

Fonctions importantes :

- `fetch_html_document()`
- `fetch_html_from_url()`
- `fetch_web_search_results()`
- `parse_market_trends_html()`
- `parse_numbeo_market_page()`
- `build_scraping_summary()`
- `save_scraped_outputs()`
- `scrape_market_trends()`

Sorties :

- `data/external/scraped_market_trends.csv`
- `data/external/scraped_market_trends_summary.json`

Commandes utiles :

```bash
python -m backend.etl.scrape_market_trends
python -m backend.etl.scrape_market_trends --search "real estate usa prices"
```

Competences :

- C1 : scraping.
- C3 : structuration et nettoyage.
- C5/C10 : enrichissement des analyses.

### `backend/etl/big_data_duckdb.py`

Role :

- Simule un traitement big data local avec DuckDB.
- Convertit les CSV en Parquet.
- Execute une requete analytique SQL sur Parquet.
- Exporte des agregations quartier/mois/style.

Fonctions importantes :

- `export_csv_to_parquet_with_duckdb()`
- `build_neighborhood_analytics()`
- `run_big_data_pipeline()`

Sorties :

- `data/lake/raw/train_bigdata.parquet`
- `data/lake/raw/test_bigdata.parquet`
- `data/lake/analytics/neighborhood_month_metrics.csv`
- `data/lake/analytics/neighborhood_month_metrics.parquet.gzip`

Commande utile :

```bash
python -m backend.etl.big_data_duckdb
```

Competences :

- C1 : source/systeme big data local.
- C2 : requetes SQL analytiques.
- C3 : aggregation.

### `backend/etl/load_to_neon.py`

Role :

- Cree le schema SQL si necessaire.
- Charge les donnees nettoyees dans PostgreSQL/Neon.
- Charge le contexte externe.
- Charge les tendances scrappees.
- Charge les resumes externes.
- Lance aussi la brique DuckDB dans `load_all_project_data()`.

Fonctions importantes :

- `load_schema()`
- `load_clean_data()`
- `load_external_market_context()`
- `load_scraped_market_trends()`
- `load_external_summary()`
- `load_all_project_data()`

Tables alimentees :

- `properties_train`
- `external_market_context`
- `scraped_market_trends`
- `external_context_summaries`

Commande utile :

```bash
python -m backend.etl.load_to_neon
```

Competences :

- C4 : creation et alimentation base.
- C5 : donnees disponibles pour API.
- C2 : insertion SQL.

### `backend/etl/run_pipeline.py`

Role :

- Orchestre tout le pipeline de donnees.
- Enchaine collecte externe, scraping, nettoyage, DuckDB et chargement base.

Ordre d'execution :

1. `fetch_external_context()`
2. `scrape_market_trends()`
3. `clean_and_save()`
4. `run_big_data_pipeline()`
5. `load_clean_data()`

Commande utile :

```bash
python -m backend.etl.run_pipeline
```

Avec recherche de tendances :

```bash
python -m backend.etl.run_pipeline --search-query "real estate usa prices"
```

Competences :

- C1 : automatisation collecte multi-sources.
- C2 : SQL/DuckDB.
- C3 : nettoyage et aggregation.
- C4 : chargement base.
- C5 : preparation pour mise a disposition API.

## Scripts base de donnees

### `backend/database/schema.sql`

Role :

- Definit les tables SQL principales.
- Sert de base au stockage Neon/PostgreSQL.

Tables :

- `properties_train`
- `model_metrics`
- `batch_predictions`
- `user_predictions`
- `external_market_context`
- `scraped_market_trends`
- `external_context_summaries`

Interet soutenance :

- Prouve l'existence d'un modele physique de donnees.
- Montre les tables dediees aux donnees, metriques, predictions et contexte externe.

Competences :

- C4 : base de donnees.
- C5 : stockage pour API.
- C11 : metriques persistantes.

### `backend/database/db.py`

Role :

- Cree le moteur SQLAlchemy utilise par les scripts ETL et ML.
- Fournit `SessionLocal`.

Interet soutenance :

- Montre que les scripts hors API partagent une connexion base centralisee.

Competences :

- C4 : connexion base.
- C11 : persistance metriques.
- C13 : execution en pipeline.

## Scripts Machine Learning

### `backend/ml/train_model.py`

Role :

- Charge les donnees d'entrainement.
- Construit un pipeline sklearn.
- Entraine un modele XGBoost.
- Calcule MAE, RMSE et R2.
- Sauvegarde le modele `.joblib`.
- Sauvegarde les metriques en base et en JSON.
- Genere un rapport de monitoring.
- Declenche une alerte si les seuils sont depasses.

Fonctions importantes :

- `load_training_data()`
- `build_pipeline()`
- `train_and_save_model()`
- `save_metrics()`
- `load_previous_metrics_snapshot()`
- `detect_training_alerts()`
- `write_monitoring_report()`
- `emit_training_alert()`
- `send_training_alert_email()`
- `dry_run_training_alert()`

Features modele :

- `GrLivArea`
- `LotArea`
- `OverallQual`
- `OverallCond`
- `BedroomAbvGr`
- `FullBath`
- `GarageCars`
- `GarageArea`
- `Neighborhood`
- `HouseStyle`
- `MoSold`
- `property_age`

Artefacts produits :

- `backend/ml/models/xgboost_model.joblib`
- `backend/ml/models/metrics.json`
- `backend/ml/models/training_monitoring_report.json`
- `backend/ml/models/training_alert.json` si alerte.

Commandes utiles :

```bash
python -m backend.ml.train_model
python -m backend.ml.train_model --dry-run-alert
```

Competences :

- C9 : modele exploitable par API.
- C11 : monitoring modele.
- C12 : tests automatises du modele.
- C13 : entrainement dans CI/CD.

### `backend/ml/predict_batch.py`

Role :

- Charge le modele sauvegarde.
- Charge les donnees de test nettoyees.
- Execute des predictions batch.
- Sauvegarde les predictions en CSV et en base.

Fonctions importantes :

- `load_model()`
- `load_test_data()`
- `save_batch_predictions()`
- `predict_batch()`

Sorties :

- `data/processed/predictions.csv`
- table `batch_predictions`

Commande utile :

```bash
python -m backend.ml.predict_batch
```

Competences :

- C9 : acces aux fonctions du modele.
- C11 : tracabilite des predictions.
- C12 : validation de batch.
- C13 : packaging/exploitation modele.

## Scripts frontend

### `frontend/src/services/api.js`

Role :

- Centralise tous les appels HTTP vers le backend.
- Configure Axios.
- Resout automatiquement `VITE_API_URL`.
- Ajoute `X-API-Key` si `VITE_API_KEY` existe.
- Transforme certaines erreurs en messages lisibles.

Fonctions importantes :

- `getMarketDashboard()`
- `getMarketFilters()`
- `predictProperty()`
- `getPredictionHistory()`
- `getLatestModelMetrics()`
- `getModelMetricsHistory()`
- `sendChatMessage()`
- `getErrorMessage()`

Competences :

- C10 : integration API dans l'application.
- C17 : communication front/back.
- C11 : affichage des metriques.

### `frontend/src/App.jsx`

Role :

- Structure les routes/pages principales de l'application.
- Oriente l'utilisateur vers les vues metier.

Pages principales :

- Marche.
- Prediction.
- Assistant IA.

Competences :

- C10 : integration dans une application.
- C17 : navigation et interfaces.

### `frontend/src/pages/MarketPage.jsx`

Role :

- Affiche les KPI de marche.
- Applique les filtres utilisateur.
- Affiche les graphiques Recharts.
- Affiche une analyse interpretable avec contexte externe.

Composants utilises :

- `MarketFilters`
- `KpiCards`
- `PriceByNeighborhoodChart`
- `PriceVsSurfaceChart`
- `PriceByQualityChart`
- `PriceDistributionChart`
- `SeasonalityChart`

Competences :

- C5 : restitution des donnees.
- C10 : consommation API.
- C17 : interface utilisateur.

### `frontend/src/pages/PredictionPage.jsx`

Role :

- Orchestre la prediction utilisateur.
- Charge les filtres, metriques, historique et KPI.
- Envoie le formulaire vers `/api/predict`.
- Affiche le resultat et la sante du modele.

Composants utilises :

- `PredictionForm`
- `PredictionResult`
- `ModelHealthSection`
- `PredictionHistory`

Competences :

- C9 : usage du modele.
- C10 : integration API modele.
- C11 : affichage sante modele.
- C17 : interface metier.

### `frontend/src/pages/AssistantPage.jsx`

Role :

- Fournit une interface de chat.
- Envoie les messages vers `/api/chat`.
- Permet un mode local ou OpenRouter selon la configuration.

Composants utilises :

- `ChatWindow`
- `QuickQuestions`

Competences :

- C8/C10 : integration service IA.
- C17 : interface applicative.

### `frontend/src/components/prediction/PredictionForm.jsx`

Role :

- Collecte les caracteristiques du bien.
- Genere le payload envoye a l'API.
- Sert de premiere validation cote client.

Champs importants :

- surface habitable.
- terrain.
- qualite generale.
- etat general.
- chambres.
- salles de bain.
- garage.
- quartier.
- style.
- mois de vente.
- age du bien.

Competences :

- C10 : integration fonctionnelle API.
- C17 : composant interface.

### `frontend/src/components/prediction/ModelHealthSection.jsx`

Role :

- Affiche les metriques du modele.
- Met en avant MAE, RMSE, R2, version et historique.

Competences :

- C11 : restitution des metriques.
- C17 : interface de supervision.

### `frontend/src/components/prediction/PredictionHistory.jsx`

Role :

- Affiche les predictions recentes.
- Permet une lecture de la tracabilite utilisateur.

Competences :

- C10 : integration API.
- C11 : historisation.
- C17 : UI.

### `frontend/src/components/market/*.jsx`

Role :

- Contient les graphiques et cartes KPI du dashboard marche.

Fichiers :

- `KpiCards.jsx`
- `MarketFilters.jsx`
- `PriceByNeighborhoodChart.jsx`
- `PriceByQualityChart.jsx`
- `PriceDistributionChart.jsx`
- `PriceVsSurfaceChart.jsx`
- `SeasonalityChart.jsx`

Competences :

- C5 : mise a disposition visuelle des donnees.
- C17 : composants frontend.

## Tests automatises

### `backend/tests/conftest.py`

Role :

- Configure l'environnement de test.
- Force une base SQLite de test.
- Cree un modele factice pour les predictions.
- Fournit le client FastAPI avec header `X-API-Key`.

Interet soutenance :

- Montre que les tests sont isoles de la production.
- Rend les tests reproductibles.

Competences :

- C12 : environnement de test.
- C18 : automatisation tests.

### `backend/tests/test_api.py`

Role :

- Teste les routes principales de l'API.
- Verifie les dashboards, filtres, chat, metriques et historique.
- Verifie que les endpoints metriques exigent une cle API.

Competences :

- C5 : endpoints data.
- C9 : routes API.
- C11 : metriques securisees.
- C12/C18 : tests automatises.

### `backend/tests/test_predict.py`

Role :

- Teste la prediction unitaire via `/api/predict`.
- Verifie que le modele renvoie un prix et une version.
- Verifie les rejets `422` pour payload invalide.

Cas invalides couverts :

- feature manquante.
- feature numerique invalide.
- feature categorielle vide.

Competences :

- C9 : API modele.
- C12 : tests de validation modele/API.

### `backend/tests/test_train_model.py`

Role :

- Teste l'entrainement du modele.
- Verifie les metriques.
- Verifie la creation de l'artefact `.joblib`.
- Verifie le declenchement d'alerte en cas de degradation simulee.

Competences :

- C11 : alertes monitoring.
- C12 : tests automatises modele.
- C13 : modele integrable en CI/CD.

### `backend/tests/test_monitoring.py`

Role :

- Teste `detect_training_alerts()`.
- Teste la generation de `training_monitoring_report.json`.
- Teste la generation de `training_alert.json`.
- Teste l'envoi d'email via SMTP factice.

Competences :

- C11 : monitorage et alertes.
- C12 : tests automatises.

### `backend/tests/test_etl.py`

Role :

- Teste le nettoyage.
- Teste la limitation du nombre de lignes.
- Teste l'orchestration du pipeline.
- Teste la presence de la brique DuckDB.

Competences :

- C1 : extraction.
- C3 : nettoyage.
- C12/C18 : tests automatises.

### `backend/tests/test_data_contract.py`

Role :

- Verifie que les colonnes attendues sont conservees.
- Verifie que les colonnes inutiles sont supprimees.

Competences :

- C3 : contrat de donnees.
- C12 : validation des donnees.

### `backend/tests/test_scraping.py`

Role :

- Teste le parsing HTML.
- Teste les resumes de scraping.
- Teste l'export Parquet.
- Teste le mode recherche web avec mocks.

Competences :

- C1 : scraping.
- C3 : structuration des donnees.
- C12 : tests automatises.

### `backend/tests/test_batch_predictions.py`

Role :

- Verifie la coherence des features batch.
- Verifie la forme des entrees de prediction batch.

Competences :

- C9 : prediction batch.
- C12 : tests automatises.

### `backend/tests/test_schemas.py`

Role :

- Teste les schemas Pydantic de metriques.
- Verifie `ModelMetricsResponse` et `ModelMetricsHistoryResponse`.

Competences :

- C9/C11 : contrats API.
- C12 : validation automatisee.

### `tests/*.py`

Role :

- Reexporte certains tests backend au niveau racine.
- Permet de lancer `python -m pytest backend/tests tests -q`.

Commande utile :

```bash
python -m pytest backend/tests tests -q
```

Resultat obtenu apres les dernieres modifications :

```text
55 passed
```

## CI/CD et livraison

### `.github/workflows/mlops-ci.yml`

Role :

- Workflow centre ML/backend.
- Installe Python.
- Installe les dependances backend.
- Lance les tests.
- Nettoie les donnees.
- Entraine le modele.
- Verifie l'existence du modele et des metriques.

Competences :

- C12 : tests automatises modele.
- C13 : chaine de livraison modele.

### `.github/workflows/ci-cd.yml`

Role :

- Workflow CI/CD plus complet.
- Prepare les assets ETL.
- Valide les schemas Pydantic.
- Lance les tests.
- Entraine le modele.
- Genere un rapport qualite.
- Build le frontend.
- Peut declencher Render via hook.

Etapes importantes :

- `Prepare ETL assets`
- `Validate Pydantic schemas`
- `Run automated tests`
- `Train model and generate monitoring report`
- `Build CI summary report`
- `Build frontend application`
- `Trigger Render deployment`

Competences :

- C12 : tests automatises.
- C13 : livraison continue modele.
- C18 : integration continue.
- C19 : livraison continue application.

## Docker et deploiement

### `Dockerfile`

Role :

- Build le frontend React.
- Installe le backend Python.
- Copie le frontend compile dans l'image.
- Lance FastAPI avec Uvicorn.

Commande utile :

```bash
docker build -t estate-ai .
docker run -p 8000:8000 estate-ai
```

Competences :

- C13 : packaging modele/service.
- C19 : packaging application.

### `backend/Dockerfile`

Role :

- Image dediee backend.
- Utile pour separer le service API.

Competences :

- C9 : service API deployable.
- C19 : packaging.

### `frontend/Dockerfile`

Role :

- Image dediee frontend.
- Build et sert l'application React.

Competences :

- C10 : application cliente deployable.
- C19 : livraison frontend.

### `docker-compose.yml`

Role :

- Lance les services en local de maniere reproductible.
- Facilite les tests d'integration manuels.

Competences :

- C17 : environnement applicatif.
- C19 : livraison locale.

### `render.yaml`

Role :

- Decrit le service Render cible.
- Configure le chemin du Dockerfile.
- Declare les variables d'environnement principales.
- Configure le healthcheck `/api/health`.

Competences :

- C19 : livraison continue/deploiement.
- C17 : application exploitable.

## Fichiers de documentation technique

### `docs/architecture.md`

Role :

- Explique l'architecture generale.
- Decrit les couches data, ML, API et frontend.

Competences :

- C15 : cadre technique.
- C17 : architecture applicative.

### `docs/data_strategy.md`

Role :

- Explique le choix des colonnes conservees.
- Justifie la reduction du dataset.
- Explique la limitation du volume.

Competences :

- C3 : nettoyage.
- C4 : minimisation des donnees.

### `docs/database_architecture.md`

Role :

- Explique les tables.
- Presente la logique de separation.
- Aborde la minimisation RGPD.

Competences :

- C4 : base de donnees et RGPD.

### `docs/model_strategy.md`

Role :

- Explique les features du modele.
- Explique le pipeline sklearn/XGBoost.
- Explique les metriques.

Competences :

- C9 : modele expose.
- C11 : metriques.
- C12 : validation modele.

### `docs/continuous_delivery.md`

Role :

- Explique la CI/CD.
- Liste les etapes automatisees.
- Liste les artefacts verifies.

Competences :

- C13 : livraison modele.
- C18 : integration continue.
- C19 : livraison application.

### `docs/competencies_mapping.md`

Role :

- Relie les fichiers du projet aux competences RNCP.
- Sert de table de correspondance pour la soutenance.

Competences :

- E1, E3 et E4.

## Ordre conseille de demonstration

### Demonstration E1

1. Montrer `backend/etl/run_pipeline.py`.
2. Montrer `backend/etl/clean_data.py`.
3. Montrer `backend/etl/fetch_external_context.py`.
4. Montrer `backend/etl/scrape_market_trends.py`.
5. Montrer `backend/etl/big_data_duckdb.py`.
6. Montrer `backend/etl/load_to_neon.py`.
7. Montrer `backend/database/schema.sql`.
8. Montrer les endpoints `market-dashboard`, `filters`, `overview`.

### Demonstration E3

1. Montrer `backend/ml/train_model.py`.
2. Montrer `backend/ml/predict_batch.py`.
3. Montrer `/api/predict` dans `backend/app/api.py`.
4. Montrer `backend/app/auth.py`.
5. Montrer `backend/tests/test_predict.py`.
6. Montrer `backend/tests/test_monitoring.py`.
7. Montrer `.github/workflows/ci-cd.yml`.
8. Montrer `ModelHealthSection.jsx`.

### Demonstration E4

1. Montrer `frontend/src/App.jsx`.
2. Montrer `frontend/src/services/api.js`.
3. Montrer `frontend/src/pages/MarketPage.jsx`.
4. Montrer `frontend/src/pages/PredictionPage.jsx`.
5. Montrer `frontend/src/pages/AssistantPage.jsx`.
6. Montrer `Dockerfile`.
7. Montrer `render.yaml`.
8. Montrer `.github/workflows/ci-cd.yml`.

## Commandes essentielles a connaitre

Installer le backend :

```bash
pip install -r backend/requirements.txt
```

Lancer l'API :

```bash
python -m uvicorn backend.app.main:app --reload
```

Nettoyer les donnees :

```bash
python -m backend.etl.clean_data
```

Lancer le pipeline data complet :

```bash
python -m backend.etl.run_pipeline
```

Charger la base :

```bash
python -m backend.etl.load_to_neon
```

Entrainer le modele :

```bash
python -m backend.ml.train_model
```

Simuler une alerte monitoring :

```bash
python -m backend.ml.train_model --dry-run-alert
```

Generer les predictions batch :

```bash
python -m backend.ml.predict_batch
```

Lancer les tests :

```bash
python -m pytest backend/tests tests -q
```

Installer et lancer le frontend :

```bash
cd frontend
npm install
npm run dev
```

Builder le frontend :

```bash
cd frontend
npm run build
```

Sous Windows PowerShell si `npm.ps1` est bloque :

```bash
npm.cmd run build
```

## Points forts a presenter

- Pipeline ETL multi-sources : CSV, API externe, scraping, DuckDB/Parquet.
- Base PostgreSQL/Neon avec schema SQL clair.
- API FastAPI avec endpoints data, prediction, metriques et chat.
- Authentification par `X-API-Key` sur routes sensibles.
- Prediction IA via modele XGBoost serialize en `.joblib`.
- Monitoring modele avec MAE, RMSE, R2, rapports JSON et alertes.
- Frontend React complet avec dashboards, prediction, historique et assistant.
- Tests automatises nombreux.
- CI/CD GitHub Actions avec tests, entrainement, monitoring report et build frontend.
- Packaging Docker et configuration Render.

## Points de vigilance a expliquer honnetement

- `/api/predict` n'utilise pas de schema Pydantic dedie pour l'entree, car le rapport E3 presente une validation explicite par `FEATURES`. Le code est donc coherent avec le rapport.
- Le monitoring est un monitoring leger adapte a un MVP : metriques, JSON, base, frontend et alerte SMTP. Prometheus/Grafana sont presentes comme perspectives, pas comme existants.
- L'authentification repose sur une cle API statique. C'est coherent avec le rapport, mais OAuth2/JWT serait une evolution industrielle.
- Les tests frontend ne sont pas aussi developpes que les tests backend/ML.

## Resume rapide pour soutenance

Estate AI dispose d'une chaine technique complete : extraction, nettoyage, stockage, entrainement, exposition API, integration frontend, monitoring, tests et CI/CD. Les scripts les plus critiques sont `run_pipeline.py`, `clean_data.py`, `load_to_neon.py`, `train_model.py`, `predict_batch.py`, `api.py`, `auth.py`, `frontend/src/services/api.js` et les workflows GitHub Actions. Ensemble, ils permettent de soutenir les blocs E1, E3 et E4 sur la partie code.
