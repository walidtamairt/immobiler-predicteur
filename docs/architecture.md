# Architecture de la plateforme immobiliere IA

## Objet

Cette application transforme un pipeline de donnees et un modele de regression immobiliere en un service numerique complet.

Le produit permet de :

- analyser le marche immobilier,
- estimer le prix d'un bien,
- journaliser les predictions,
- afficher des indicateurs lisibles pour un utilisateur non technique,
- enrichir l'experience avec un assistant IA contextualise.

## Utilisateurs cibles

- **Acheteurs** : estimer un bien et comparer son niveau de prix au marche.
- **Investisseurs** : identifier les zones et profils de biens interessants.
- **Agences** : appuyer un argumentaire commercial avec des indicateurs data.

## Vue d'ensemble de l'architecture

Le projet repose sur quatre blocs principaux :

1. **Couche data**
   - ingestion des fichiers sources,
   - nettoyage et normalisation,
   - chargement dans Neon PostgreSQL.
2. **Couche machine learning**
   - entrainement du modele XGBoost,
   - calcul des metriques,
   - sauvegarde de l'artefact et de la version.
3. **Couche API**
   - mise a disposition des donnees de marche,
   - exposition du modele via REST,
   - acces aux metriques et a l'historique,
   - endpoint de chat.
4. **Couche frontend**
   - application React / Vite,
   - 3 onglets : `Marche`, `Prediction`, `Assistant IA`,
   - restitution metier des analyses et predictions.

## Organisation des repertoires

- `backend/app`
  - API FastAPI,
  - logique metier,
  - acces base,
  - schemas,
  - modeles ORM.
- `backend/etl`
  - ingestion,
  - nettoyage,
  - chargement en base,
  - collecte externe complementaire.
- `backend/ml`
  - entrainement,
  - evaluation,
  - predictions batch,
  - artefacts de modele.
- `backend/database`
  - schema SQL et point d'acces historique a la base.
- `frontend`
  - application React,
  - composants UI,
  - pages metier,
  - services d'appel API.
- `docs`
  - documentation d'architecture,
  - strategie data,
  - strategie modele,
  - validation des competences,
  - deploiement et delivery.

## Flux de fonctionnement

### 1. Preparation des donnees

- lecture de `data/train.csv` et `data/test.csv`,
- verification des colonnes,
- nettoyage,
- creation de `property_age`,
- generation des fichiers nettoyes.

### 2. Stockage cloud

- les donnees nettoyees sont chargees dans Neon,
- la table principale est `properties_train`,
- les tables `model_metrics`, `batch_predictions` et `user_predictions` assurent la tracabilite.

### 3. Entrainement du modele

- l'entrainement lit les donnees depuis PostgreSQL,
- le preprocessing est gere par `sklearn`,
- le modele XGBoost est entraine,
- les metriques sont calculees puis stockees,
- l'artefact du modele est sauvegarde localement dans le projet.

### 4. Exposition API

L'API FastAPI expose notamment :

- `GET /api/market-dashboard`
- `GET /api/filters`
- `POST /api/predict`
- `GET /api/prediction-history`
- `GET /api/model-metrics/latest`
- `GET /api/model-metrics/history`
- `POST /api/chat`

### 5. Restitution frontend

Le frontend consomme uniquement l'API.

- l'onglet `Marche` affiche KPI, dashboards et synthese,
- l'onglet `Prediction` propose le formulaire, le resultat, la sante du modele et l'historique,
- l'onglet `Assistant IA` offre un chat contextualise par les donnees de marche.

## Donnees externes complementaires

Le projet comprend une collecte externe ponctuelle via :

- [fetch_external_context.py](/d:/Projet estate/backend/etl/fetch_external_context.py:1)

Cette brique ne remplace pas le dataset principal. Elle enrichit le contexte marche pour l'assistant IA et le bloc d'analyse.

## Stockage et persistance

Le stockage durable repose sur Neon PostgreSQL.

Les fichiers locaux servent a :

- l'ingestion initiale,
- l'entrainement,
- la generation d'artefacts.

Les elements persistants utiles a l'application en production sont centralises dans Neon :

- donnees metier,
- historique de predictions,
- metriques du modele.

## Securite et configuration

La configuration est externalisee dans `.env` :

- `DATABASE_URL`
- `MODEL_PATH`
- `MODEL_VERSION`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`

Cette approche evite les secrets dans le code et facilite la reproductibilite.

## Deploiement cible

- **Base de donnees** : Neon PostgreSQL
- **Backend** : Render
- **Frontend** : Render
- **Conteneurisation** : Docker et `docker-compose`

## Conclusion

L'architecture du projet est volontairement simple, modulaire et presentable.

Elle demontre une separation nette entre :

- la preparation des donnees,
- l'exploitation du modele,
- les services d'API,
- l'experience utilisateur.

Cette organisation rend le projet defendable aussi bien techniquement qu'en contexte de certification.
