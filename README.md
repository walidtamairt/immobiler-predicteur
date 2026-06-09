# Plateforme IA immobiliere

## Vue rapide

Le projet est une application complete de prediction et d'analyse immobiliere construite autour de :

- un pipeline ETL,
- une base Neon PostgreSQL,
- un modele XGBoost,
- une API FastAPI,
- un frontend React / Vite,
- un assistant IA contextualise.

## Documentation principale

- [RAPPORT_GENERAL.md](/d:/Projet estate/RAPPORT_GENERAL.md:1)
- [docs/architecture.md](/d:/Projet estate/docs/architecture.md:1)
- [docs/competencies_mapping.md](/d:/Projet estate/docs/competencies_mapping.md:1)
- [docs/continuous_delivery.md](/d:/Projet estate/docs/continuous_delivery.md:1)
- [docs/agile_project_management.md](/d:/Projet estate/docs/agile_project_management.md:1)

## Fonctionnement du projet

### Pipeline data et ML

```bash
python -m backend.etl.clean_data
python -m backend.etl.load_to_neon
python -m backend.ml.train_model
python -m backend.ml.predict_batch
```

### Lancement du backend

```bash
python -m uvicorn backend.app.main:app --reload
```

### Lancement du frontend

```bash
cd frontend
npm install
npm run dev
```

## Fichiers produits

- `data/processed/train_clean.csv`
- `data/processed/test_clean.csv`
- `data/processed/predictions.csv`
- `backend/ml/models/xgboost_model.joblib`
- `backend/ml/models/metrics.json`

## Deploiement cible

- **Base** : Neon PostgreSQL
- **Backend** : Render en conteneur Docker
- **Frontend** : Render en conteneur Docker

Les fichiers de deploiement disponibles sont :

- [render.yaml](/d:/Projet estate/render.yaml:1)
- [docker-compose.yml](/d:/Projet estate/docker-compose.yml:1)
- [backend/Dockerfile](/d:/Projet estate/backend/Dockerfile:1)
- [frontend/Dockerfile](/d:/Projet estate/frontend/Dockerfile:1)

## Positionnement RNCP

Le projet a ete cadre prioritairement pour soutenir les blocs :

- **E1** : collecte, stockage et mise a disposition des donnees,
- **E3** : integration, exposition et fiabilisation du modele IA,
- **E4** : conception, developpement, test et livraison de l'application.
