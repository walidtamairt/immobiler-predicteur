# Rapport General - Plateforme IA de Prediction et d'Analyse Immobiliere

## 1. Objet du projet

Ce projet est une application complete de data engineering, machine learning et developpement full-stack appliquee au secteur immobilier.

L'objectif est de proposer une plateforme capable de :

- analyser un marche immobilier a partir de donnees structurees,
- predire le prix d'un bien,
- exposer les traitements via une API REST,
- stocker les donnees et les resultats dans une base cloud,
- restituer les informations dans une interface web exploitable,
- enrichir l'experience utilisateur avec un assistant IA contextualise.

Le projet a ete cadre pour soutenir prioritairement la validation des blocs **E1**, **E3** et **E4** du parcours RNCP Developpeur en Intelligence Artificielle.

---

## 2. Besoin metier et utilisateurs cibles

### Besoin metier

Le besoin metier consiste a transformer un jeu de donnees immobiliere brut en un service numerique exploitable par des utilisateurs non techniques.

La plateforme doit permettre :

- de mieux comprendre le niveau de prix d'un marche,
- d'estimer un bien a partir de ses caracteristiques,
- de capitaliser les predictions et les metriques du modele,
- de rendre les analyses accessibles via dashboards et API.

### Utilisateurs cibles

- **Acheteurs** : comparer un bien a la moyenne du marche et estimer sa valeur.
- **Investisseurs** : identifier les zones ou les profils de biens potentiellement attractifs.
- **Agences** : disposer d'un outil d'aide a la vente et d'argumentation base sur la donnee.

---

## 3. Fonctionnalites de l'application

### 3.1 Onglet Marche

L'onglet `Marche` permet de visualiser les indicateurs immobiliers et de filtrer le perimetre d'analyse.

Fonctionnalites disponibles :

- filtres par quartier, style de maison, qualite, chambres, salles de bain, mois de vente et age du bien,
- KPI de marche :
  - nombre total de biens,
  - prix moyen,
  - prix median,
  - surface moyenne,
  - prix moyen au pied carre,
- dashboards :
  - prix moyen par quartier,
  - prix vs surface habitable,
  - prix moyen par niveau de qualite,
  - distribution des prix,
  - saisonnalite des prix,
- bloc d'analyse de marche en bas de page,
- integration d'un contexte externe si disponible.

### 3.2 Onglet Prediction

L'onglet `Prediction` permet de saisir les caracteristiques d'un bien et d'obtenir une estimation interpretable.

Fonctionnalites disponibles :

- formulaire utilisateur avec des libelles metier comprehensibles,
- appel au modele via l'API,
- restitution de :
  - prix estime,
  - borne basse,
  - borne haute,
  - version du modele,
  - texte d'interpretation,
- affichage de la sante du modele :
  - version,
  - MAE,
  - RMSE,
  - R2,
  - date du dernier entrainement,
  - nombre de lignes d'entrainement,
  - nombre de variables,
- historique recent des predictions utilisateur.

### 3.3 Onglet Assistant IA

L'onglet `Assistant IA` permet d'interroger l'application en langage naturel.

Fonctionnalites disponibles :

- interface de chat,
- questions rapides pour orienter la demonstration,
- synthese des indicateurs de marche injectee dans le contexte,
- reponse en mode distant via OpenRouter si la cle est configuree,
- reponse locale de secours si la cle n'est pas disponible,
- reprise du contexte externe lorsqu'il existe.

---

## 4. Architecture technique

Le projet suit une separation claire entre la donnee, le modele, l'API et l'interface.

### Backend

- `backend/app`
  - API FastAPI
  - logique metier
  - endpoints d'analyse, prediction et assistant IA
- `backend/etl`
  - ingestion
  - nettoyage
  - chargement vers Neon
  - collecte externe complementaire
- `backend/ml`
  - entrainement du modele
  - evaluation
  - versioning
  - predictions batch
- `backend/database`
  - schema SQL
  - acces unifie a la base

### Frontend

- application React / Vite
- 3 onglets obligatoires :
  - `Marche`
  - `Prediction`
  - `Assistant IA`
- composants reutilisables :
  - navigation
  - cartes KPI
  - cartes de graphes
  - formulaire
  - fenetre de chat

### Base de donnees

- Neon PostgreSQL comme stockage cloud central
- tables principales :
  - `properties_train`
  - `model_metrics`
  - `batch_predictions`
  - `user_predictions`

### Deploiement

- backend : Render
- frontend : Render
- base : Neon PostgreSQL
- conteneurisation :
  - `backend/Dockerfile`
  - `frontend/Dockerfile`
  - `docker-compose.yml`
  - `render.yaml`

---

## 5. Flux de fonctionnement de bout en bout

### 5.1 Preparation des donnees

1. Lecture des donnees source dans `data/train.csv` et `data/test.csv`
2. Validation de la structure des fichiers
3. Nettoyage et reduction des variables
4. Creation de la variable `property_age`
5. Production des fichiers nettoyes dans `data/processed`

### 5.2 Stockage cloud

1. Lecture des fichiers nettoyes
2. Insertion des lignes utiles dans Neon
3. Mise a disposition des donnees pour le backend, le ML et les dashboards

### 5.3 Entrainement du modele

1. Lecture des donnees depuis PostgreSQL
2. Separation features / cible
3. Preprocessing des variables numeriques et categorielles
4. Entrainement du modele XGBoost
5. Calcul des metriques
6. Sauvegarde du modele et des metriques

### 5.4 Exposition API

L'API met a disposition :

- donnees de marche,
- filtres,
- dashboards,
- prediction unitaire,
- historique de prediction,
- metriques du modele,
- conversation assistant IA.

### 5.5 Experience utilisateur

Le frontend consomme exclusivement l'API existante.

- les dashboards lisent Neon via le backend,
- le formulaire appelle le modele via `POST /api/predict`,
- l'assistant IA consomme `POST /api/chat`,
- l'utilisateur ne manipule jamais directement les CSV.

---

## 6. Comment chaque grande brique est assuree

### 6.1 Collecte et ingestion

Assuree par :

- [backend/etl/ingest_data.py](/d:/Projet estate/backend/etl/ingest_data.py:1)
- [backend/etl/clean_data.py](/d:/Projet estate/backend/etl/clean_data.py:1)

Cette brique assure :

- le chargement des fichiers CSV,
- le controle des colonnes attendues,
- la gestion des erreurs de lecture,
- la preparation avant traitement.

### 6.2 Nettoyage et transformation

Assuree par :

- [backend/etl/clean_data.py](/d:/Projet estate/backend/etl/clean_data.py:1)

Cette brique assure :

- suppression des valeurs aberrantes,
- gestion des valeurs manquantes,
- reduction des colonnes a forte valeur metier,
- normalisation des donnees pour l'analyse et le ML.

### 6.3 Stockage et persistance

Assures par :

- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)
- [backend/app/database.py](/d:/Projet estate/backend/app/database.py:1)
- [backend/etl/load_to_neon.py](/d:/Projet estate/backend/etl/load_to_neon.py:1)

Cette brique assure :

- un stockage centralise en cloud,
- une separation entre donnees metier, metriques et predictions,
- une reutilisation des memes tables par toute l'application.

### 6.4 Modele de prediction

Assure par :

- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)

Cette brique assure :

- la lecture des donnees depuis la base,
- le preprocessing,
- l'entrainement,
- l'evaluation,
- le versioning,
- la sauvegarde de l'artefact.

### 6.5 Inference et journalisation

Assurees par :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [backend/app/models.py](/d:/Projet estate/backend/app/models.py:1)

Cette brique assure :

- l'exposition du modele via `POST /api/predict`,
- le retour d'une prediction interpretable,
- la journalisation des predictions utilisateur,
- la tracabilite des versions du modele.

### 6.6 Dashboards et UX

Assures par :

- [frontend/src/pages/MarketPage.jsx](/d:/Projet estate/frontend/src/pages/MarketPage.jsx:1)
- [frontend/src/pages/PredictionPage.jsx](/d:/Projet estate/frontend/src/pages/PredictionPage.jsx:1)
- [frontend/src/pages/AssistantPage.jsx](/d:/Projet estate/frontend/src/pages/AssistantPage.jsx:1)

Cette brique assure :

- la restitution visuelle des analyses,
- une experience utilisateur metier,
- une navigation limitee a 3 onglets clairs,
- des libelles comprehensibles pour un public non technique.

### 6.7 Assistant IA

Assure par :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [frontend/src/components/assistant/ChatWindow.jsx](/d:/Projet estate/frontend/src/components/assistant/ChatWindow.jsx:1)
- [frontend/src/components/assistant/QuickQuestions.jsx](/d:/Projet estate/frontend/src/components/assistant/QuickQuestions.jsx:1)

Cette brique assure :

- un dialogue contextualise,
- une exploitation du resume de marche issu de Neon,
- une continuite de service meme sans cle OpenRouter grace au mode local.

### 6.8 Donnees externes complementaires

Assurees par :

- [backend/etl/fetch_external_context.py](/d:/Projet estate/backend/etl/fetch_external_context.py:1)
- [data/external/external_market_summary.json](/d:/Projet estate/data/external/external_market_summary.json:1)

Cette brique assure :

- la collecte ponctuelle d'un contexte macroeconomique externe,
- sa transformation en CSV et resume JSON,
- son integration dans l'assistant IA et l'analyse de marche.

### 6.9 Qualite, tests et CI

Assures par :

- [backend/tests](/d:/Projet estate/backend/tests:1)
- [.github/workflows/mlops-ci.yml](/d:/Projet estate/.github/workflows/mlops-ci.yml:1)

Cette brique assure :

- la verification des endpoints,
- la verification du pipeline data/ML,
- la validation automatisee en integration continue,
- la verification de la presence du modele et des metriques.

---

## 7. Endpoints principaux exposes par le backend

### Data et dashboards

- `GET /api/health`
- `GET /api/market-data`
- `GET /api/market-dashboard`
- `GET /api/overview`
- `GET /api/filters`
- `GET /api/price-analysis`
- `GET /api/location-analysis`

### Prediction et monitoring

- `POST /api/predict`
- `GET /api/prediction-history`
- `GET /api/batch-predictions`
- `GET /api/model-metrics/latest`
- `GET /api/model-metrics/history`

### Assistant IA

- `POST /api/chat`

---

## 8. Procedure d'execution

### Pipeline data et ML

```bash
python -m backend.etl.clean_data
python -m backend.etl.load_to_neon
python -m backend.ml.train_model
python -m backend.ml.predict_batch
```

### Backend

```bash
python -m uvicorn backend.app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 9. Validation des competences E1

Le bloc E1 porte sur la collecte, le stockage et la mise a disposition des donnees.

### C1 - Automatiser l'extraction de donnees

Le projet automatise :

- la lecture des fichiers de donnees,
- la collecte externe complementaire via API,
- la preparation de donnees reutilisables.

Preuves :

- [backend/etl/ingest_data.py](/d:/Projet estate/backend/etl/ingest_data.py:1)
- [backend/etl/fetch_external_context.py](/d:/Projet estate/backend/etl/fetch_external_context.py:1)

### C2 - Developper des requetes SQL

Le projet exploite PostgreSQL via SQLAlchemy pour extraire, filtrer et agreger les donnees au service des dashboards et de l'API.

Preuves :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)

### C3 - Developper des regles d'agregation et de nettoyage

Le projet met en oeuvre un ETL reproductible :

- nettoyage,
- normalisation,
- reduction de colonnes,
- suppression d'outliers,
- creation de variables derivees.

Preuve :

- [backend/etl/clean_data.py](/d:/Projet estate/backend/etl/clean_data.py:1)

### C4 - Creer une base de donnees conforme au projet

Le projet modelise et utilise une base relationnelle cloud avec import automatise et configuration separee.

Preuves :

- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)
- [backend/etl/load_to_neon.py](/d:/Projet estate/backend/etl/load_to_neon.py:1)
- [.env.example](/d:/Projet estate/.env.example:1)
- [docs/database_architecture.md](/d:/Projet estate/docs/database_architecture.md:1)

### C5 - Developper une API de mise a disposition des donnees

Le projet expose des endpoints REST directement utilisables par le frontend.

Preuve :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

**Conclusion E1** :
Le projet valide E1 car il couvre la chaine complete de collecte, transformation, stockage cloud et exposition API.

---

## 10. Validation des competences E3

Dans le cadre de ce projet, E3 correspond a l'integration et a l'exploitation d'un modele IA dans un service reel.

### Entrainement du modele

Le modele XGBoost est entraine a partir des donnees stockees en base.

Preuve :

- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)

### Evaluation

Le projet mesure et conserve :

- MAE
- RMSE
- R2

Preuves :

- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)
- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)

### Versioning

Le modele est versionne avec `MODEL_VERSION`.

Preuves :

- [backend/config/settings.py](/d:/Projet estate/backend/config/settings.py:1)
- [.env.example](/d:/Projet estate/.env.example:1)

### Exposition du modele via API

Le modele est rendu accessible par `POST /api/predict`.

Preuves :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [frontend/src/pages/PredictionPage.jsx](/d:/Projet estate/frontend/src/pages/PredictionPage.jsx:1)

### Tracabilite et logs

Les predictions utilisateur sont historisees.

Preuves :

- [backend/app/models.py](/d:/Projet estate/backend/app/models.py:1)
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

**Conclusion E3** :
Le projet valide E3 car il ne s'arrete pas a un entrainement local. Il industrialise le modele, le mesure, le versionne, l'expose et journalise ses usages.

---

## 11. Validation des competences E4

Le bloc E4 porte sur la conception, le developpement, le test et la livraison d'une application integrant de l'IA.

### Analyse du besoin et architecture

Le besoin metier est documente et traduit en architecture applicative.

Preuves :

- [docs/architecture.md](/d:/Projet estate/docs/architecture.md:1)
- [docs/data_strategy.md](/d:/Projet estate/docs/data_strategy.md:1)
- [docs/model_strategy.md](/d:/Projet estate/docs/model_strategy.md:1)

### Interfaces et composants applicatifs

Le frontend React structure l'application en 3 onglets metier.

Preuves :

- [frontend/src/pages/MarketPage.jsx](/d:/Projet estate/frontend/src/pages/MarketPage.jsx:1)
- [frontend/src/pages/PredictionPage.jsx](/d:/Projet estate/frontend/src/pages/PredictionPage.jsx:1)
- [frontend/src/pages/AssistantPage.jsx](/d:/Projet estate/frontend/src/pages/AssistantPage.jsx:1)

### Integration front / back

Le frontend consomme une API stable sans acces direct aux CSV.

Preuves :

- [frontend/src/services/api.js](/d:/Projet estate/frontend/src/services/api.js:1)
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

### Tests automatises

Le projet comporte des tests backend et une execution CI.

Preuves :

- [backend/tests/test_api.py](/d:/Projet estate/backend/tests/test_api.py:1)
- [backend/tests/test_train_model.py](/d:/Projet estate/backend/tests/test_train_model.py:1)
- [.github/workflows/mlops-ci.yml](/d:/Projet estate/.github/workflows/mlops-ci.yml:1)

### Livraison et deploiement

Le projet est prevu pour Render, Neon et Docker.

Preuves :

- [render.yaml](/d:/Projet estate/render.yaml:1)
- [docker-compose.yml](/d:/Projet estate/docker-compose.yml:1)
- [backend/Dockerfile](/d:/Projet estate/backend/Dockerfile:1)
- [frontend/Dockerfile](/d:/Projet estate/frontend/Dockerfile:1)
- [docs/continuous_delivery.md](/d:/Projet estate/docs/continuous_delivery.md:1)

### Pilotage et cadre Agile

Le projet dispose aussi d'une documentation de pilotage.

Preuve :

- [docs/agile_project_management.md](/d:/Projet estate/docs/agile_project_management.md:1)

**Conclusion E4** :
Le projet valide E4 car il propose une vraie application IA complete, testable, deployable et orientee utilisateur final.

---

## 12. Forces du projet pour l'examen

- Le projet couvre toute la chaine de valeur IA : donnees, modele, API, interface, deploiement.
- Il s'appuie sur une base cloud reelle et non sur une simple demonstration locale.
- Il expose un modele IA utilisable dans une application concrete.
- Il comprend une experience utilisateur complete avec dashboards, prediction et assistant IA.
- Il produit des preuves techniques exploitables en dossier et en soutenance.

---

## 13. Synthese finale

Cette application est une plateforme immobiliere IA coherente, modulaire et presentable en contexte RNCP.

Elle montre que le candidat est capable de :

- preparer et structurer les donnees,
- stocker et exposer les informations utilement,
- entrainer et exploiter un modele de regression,
- integrer ce modele dans une application web,
- documenter, tester et preparer le deploiement.

En l'etat, ce projet constitue un **rapport de preuve solide pour E1, E3 et E4**.
