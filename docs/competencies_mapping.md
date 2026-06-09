# Validation des competences E1, E3 et E4

## Objet du document

Ce document explique comment le projet actuel permet de defender les blocs **E1**, **E3** et **E4** dans un dossier ou une soutenance RNCP.

L'approche retenue est la suivante :

- partir du fonctionnement reel du projet,
- identifier les preuves presentes dans le code et la documentation,
- relier ces preuves aux attentes de chaque bloc de competences.

## Vue d'ensemble du projet

Le projet est une plateforme immobiliere IA qui :

- prepare et nettoie des donnees immobiliere,
- les stocke dans Neon PostgreSQL,
- entraine un modele XGBoost,
- expose les traitements via FastAPI,
- restitue les analyses dans un frontend React,
- journalise et monitorise les predictions,
- propose un assistant IA contextualise.

## E1 - Collecte, stockage et mise a disposition des donnees

### C1 - Automatiser l'extraction de donnees

Le projet automatise deux types de collecte :

- la lecture de fichiers CSV immobiliers,
- la collecte externe complementaire via API.

Preuves :

- [backend/etl/ingest_data.py](/d:/Projet estate/backend/etl/ingest_data.py:1)
- [backend/etl/fetch_external_context.py](/d:/Projet estate/backend/etl/fetch_external_context.py:1)

Ce que cela permet de defendre :

- lecture automatisee de donnees source,
- gestion des erreurs,
- collecte scriptable et reproductible.

### C2 - Developper des requetes SQL

Le projet exploite PostgreSQL via SQLAlchemy pour :

- extraire les donnees de marche,
- calculer les agrégations utiles aux dashboards,
- recuperer metriques et historiques.

Preuves :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)

Ce que cela permet de defendre :

- usage reel d'une base relationnelle,
- filtrage et agrégation des donnees,
- mise a disposition structuree pour l'application.

### C3 - Developper des regles d'agregation et de nettoyage

Le pipeline ETL :

- nettoie les jeux de donnees,
- supprime les lignes aberrantes,
- gere les valeurs manquantes,
- reduit les colonnes a forte valeur metier,
- construit `property_age`.

Preuve :

- [backend/etl/clean_data.py](/d:/Projet estate/backend/etl/clean_data.py:1)

Ce que cela permet de defendre :

- un ETL reproductible,
- une preparation serieuse des donnees avant exploitation,
- une homogenisation des donnees pour le ML et les dashboards.

### C4 - Creer une base de donnees conforme au projet

Le projet utilise Neon PostgreSQL comme base cloud principale.

Preuves :

- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)
- [backend/etl/load_to_neon.py](/d:/Projet estate/backend/etl/load_to_neon.py:1)
- [docs/database_architecture.md](/d:/Projet estate/docs/database_architecture.md:1)
- [.env.example](/d:/Projet estate/.env.example:1)

Ce que cela permet de defendre :

- modelisation relationnelle simple mais claire,
- separation des tables metier et techniques,
- chargement automatise,
- externalisation de la configuration.

### C5 - Developper une API mettant les donnees a disposition

Le backend expose des endpoints REST exploitables directement par le frontend.

Preuve principale :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

Endpoints de preuve :

- `GET /api/market-dashboard`
- `GET /api/filters`
- `GET /api/overview`
- `GET /api/location-analysis`

### Conclusion E1

Le projet permet de defendre E1 de facon solide car il couvre la chaine :

- collecte,
- nettoyage,
- stockage,
- exposition des donnees.

## E3 - Integration et exploitation du modele IA

### Entrainement du modele

Le modele de regression est entraine dans :

- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)

Caracteristiques :

- `XGBRegressor`,
- pipeline `sklearn`,
- `ColumnTransformer`,
- `OneHotEncoder`,
- `SimpleImputer`.

### Evaluation

Les metriques calculees sont :

- `MAE`,
- `RMSE`,
- `R2`.

Preuves :

- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)
- [backend/database/schema.sql](/d:/Projet estate/backend/database/schema.sql:1)

Ce que cela permet de defendre :

- evaluation objective du modele,
- conservation des resultats dans la duree,
- base de monitorage.

### Versioning du modele

Le versioning repose sur :

- `MODEL_VERSION`
- l'artefact du modele,
- la conservation de la version dans les predictions et metriques.

Preuves :

- [backend/config/settings.py](/d:/Projet estate/backend/config/settings.py:1)
- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1)
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

### Exposition du modele via API

Le modele est rendu exploitable par :

- `POST /api/predict`

Preuves :

- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)
- [frontend/src/pages/PredictionPage.jsx](/d:/Projet estate/frontend/src/pages/PredictionPage.jsx:1)

Ce que cela permet de defendre :

- passage d'un modele experimental a un service IA exploitable,
- entree / sortie standardisee,
- reutilisation dans une application.

### Journalisation et suivi

Les predictions utilisateur sont conservees en base.

Preuves :

- [backend/app/models.py](/d:/Projet estate/backend/app/models.py:1)
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

Ce que cela permet de defendre :

- tracabilite,
- audit fonctionnel,
- base future de feedback loop.

### Tests automatises et fiabilite

Le projet dispose d'une suite de tests backend et ML.

Preuves :

- [backend/tests/test_api.py](/d:/Projet estate/backend/tests/test_api.py:1)
- [backend/tests/test_train_model.py](/d:/Projet estate/backend/tests/test_train_model.py:1)
- [backend/tests/test_predict.py](/d:/Projet estate/backend/tests/test_predict.py:1)
- [backend/tests/test_batch_predictions.py](/d:/Projet estate/backend/tests/test_batch_predictions.py:1)
- [backend/tests/test_data_contract.py](/d:/Projet estate/backend/tests/test_data_contract.py:1)

Point de defense recommande :

- la competence est defendable car les tests sont automatises, versionnes et executes en CI,
- la couverture est surtout backend et pipeline,
- la couverture frontend et end-to-end reste plus legere.

### Conclusion E3

Le projet permet de defendre E3 car le modele n'est pas seulement entraine :

- il est evalue,
- versionne,
- expose,
- journalise,
- monitoré,
- et verifie par des tests automatises.

## E4 - Conception, developpement et livraison de l'application

### Analyse du besoin et architecture

Le besoin metier est documente et relie a une architecture concrete.

Preuves :

- [docs/architecture.md](/d:/Projet estate/docs/architecture.md:1)
- [docs/data_strategy.md](/d:/Projet estate/docs/data_strategy.md:1)
- [docs/model_strategy.md](/d:/Projet estate/docs/model_strategy.md:1)

### Interfaces et experience utilisateur

Le frontend est organise en 3 onglets metier :

- `Marche`
- `Prediction`
- `Assistant IA`

Preuves :

- [frontend/src/pages/MarketPage.jsx](/d:/Projet estate/frontend/src/pages/MarketPage.jsx:1)
- [frontend/src/pages/PredictionPage.jsx](/d:/Projet estate/frontend/src/pages/PredictionPage.jsx:1)
- [frontend/src/pages/AssistantPage.jsx](/d:/Projet estate/frontend/src/pages/AssistantPage.jsx:1)

Ce que cela permet de defendre :

- une vraie experience utilisateur,
- une traduction du besoin en interfaces exploitables,
- une mise en produit claire du modele.

### Integration front / back

Le frontend consomme une couche API centralisee.

Preuves :

- [frontend/src/services/api.js](/d:/Projet estate/frontend/src/services/api.js:1)
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1)

### Tests et qualite applicative

Preuves :

- [backend/tests](/d:/Projet estate/backend/tests:1)
- [.github/workflows/mlops-ci.yml](/d:/Projet estate/.github/workflows/mlops-ci.yml:1)

Ce que cela permet de defendre :

- verification automatique des briques principales,
- validation du code avant progression,
- demarche de qualite logicielle.

### Livraison continue et deploiement

Preuves :

- [docs/continuous_delivery.md](/d:/Projet estate/docs/continuous_delivery.md:1)
- [render.yaml](/d:/Projet estate/render.yaml:1)
- [docker-compose.yml](/d:/Projet estate/docker-compose.yml:1)
- [backend/Dockerfile](/d:/Projet estate/backend/Dockerfile:1)
- [frontend/Dockerfile](/d:/Projet estate/frontend/Dockerfile:1)

Ce que cela permet de defendre :

- une application prete a etre empaquetee,
- une chaine de verification automatisée,
- une logique de deploiement cloud coherente.

### Pilotage Agile

Preuve :

- [docs/agile_project_management.md](/d:/Projet estate/docs/agile_project_management.md:1)

### Conclusion E4

Le projet permet de defendre E4 car il montre :

- une application complete,
- une interface exploitable,
- une integration claire entre donnees, modele et service,
- des tests,
- une chaine de livraison,
- une documentation presentable.

## Synthese finale

Le projet constitue une base serieuse pour soutenir :

- **E1** : collecte, stockage et mise a disposition des donnees,
- **E3** : integration, exposition et fiabilisation du modele,
- **E4** : conception, developpement, test et livraison d'une application IA.

La force principale du dossier est de montrer non pas un simple modele, mais un **service IA exploitable de bout en bout**.
