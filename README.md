# Plateforme IA immobiliere

Estate AI est une application full-stack d'analyse et de prediction immobiliere. Le projet assemble un pipeline ETL, une base PostgreSQL, un modele XGBoost, une API FastAPI et un frontend React/Vite dans une meme chaine applicative.

## Vue d'ensemble

L'application couvre trois usages principaux :

- consulter des indicateurs et visualisations de marche ;
- estimer un bien immobilier via un modele de regression ;
- interroger un assistant qui s'appuie sur le contexte de marche disponible et, si configure, sur OpenRouter.

Le backend peut aussi servir le frontend compile en production via FastAPI.

## Stack technique

- Backend : FastAPI, SQLAlchemy, Pydantic Settings
- Frontend : React 19, Vite, Recharts
- Donnees et ML : pandas, DuckDB, scikit-learn, XGBoost, joblib
- Base de donnees : PostgreSQL / Neon
- Livraison : Docker, Render, GitHub Actions

## Structure utile

- [backend/app/main.py](/d:/Projet estate/backend/app/main.py:1) : point d'entree FastAPI
- [backend/app/api.py](/d:/Projet estate/backend/app/api.py:1) : routes API
- [backend/config/settings.py](/d:/Projet estate/backend/config/settings.py:1) : configuration via variables d'environnement
- [backend/etl](/d:/Projet estate/backend/etl:1) : nettoyage et chargement des donnees
- [backend/ml/train_model.py](/d:/Projet estate/backend/ml/train_model.py:1) : entrainement du modele
- [frontend/src](/d:/Projet estate/frontend/src:1) : application React
- [.github/workflows](/d:/Projet estate/.github/workflows:1) : workflows CI/CD
- [render.yaml](/d:/Projet estate/render.yaml:1) : cible Render

## Demarrage rapide

### 1. Variables d'environnement

Le projet lit sa configuration depuis un fichier `.env` a la racine. Un exemple est fourni dans [.env.example](/d:/Projet estate/.env.example:1).

Variables utiles :

- `DATABASE_URL` : URL de connexion principale a la base
- `MODEL_PATH` : chemin du modele joblib utilise par l'API
- `API_KEY` : cle attendue par les routes protegees du backend
- `VITE_API_URL` : URL du backend pour le frontend en developpement
- `VITE_API_KEY` : cle envoyee par le frontend dans le header `X-API-Key`
- `OPENROUTER_API_KEY` : cle optionnelle pour activer l'assistant distant

### 2. Backend

Installation des dependances :

```bash
pip install -r backend/requirements.txt
```

Lancement du serveur :

```bash
python -m uvicorn backend.app.main:app --reload
```

API locale par defaut :

```text
http://localhost:8000
```

### 3. Frontend

Installation et lancement :

```bash
cd frontend
npm install
npm run dev
```

Frontend local par defaut :

```text
http://localhost:5173
```

Sans `VITE_API_URL`, le frontend pointe automatiquement vers `http://localhost:8000` quand il tourne en local.

## Pipeline data et modele

Commandes typiques :

```bash
python -m backend.etl.clean_data
python -m backend.etl.load_to_neon
python -m backend.ml.train_model
python -m backend.ml.predict_batch
```

Artefacts produits ou verifies par le projet :

- `data/lake/processed/train_clean.parquet.gzip`
- `data/lake/processed/test_clean.parquet.gzip`
- `backend/ml/models/xgboost_model.joblib`
- `backend/ml/models/metrics.json`
- `backend/ml/models/training_monitoring_report.json`

## Authentification API

Certaines routes sont protegees par un header `X-API-Key`. La valeur attendue cote backend vient de `API_KEY`, et le frontend peut envoyer cette valeur via `VITE_API_KEY`.

Le controle est defini dans [backend/app/auth.py](/d:/Projet estate/backend/app/auth.py:1).

## Tests

Les tests backend vivent principalement dans [backend/tests](/d:/Projet estate/backend/tests:1) et [tests](/d:/Projet estate/tests:1).

Execution locale :

```bash
python -m pytest backend/tests tests -q
```

Les tests utilisent une configuration de base de donnees et de modele dediee definie dans [backend/tests/conftest.py](/d:/Projet estate/backend/tests/conftest.py:1).

## CI/CD

Le depot contient deux workflows GitHub Actions :

- [mlops-ci.yml](/d:/Projet estate/.github/workflows/mlops-ci.yml:1) :
  workflow CI centre sur le backend et le modele. Il installe Python, lance les tests backend, nettoie les donnees, entraine le modele et verifie la presence des artefacts principaux.
- [ci-cd.yml](/d:/Projet estate/.github/workflows/ci-cd.yml:1) :
  workflow plus complet qui verifie le backend, prepare des assets ETL, valide les schemas Pydantic, lance les tests, entraine le modele, genere un rapport qualite, build le frontend et peut declencher le deploiement Render.

Declencheurs actuels :

- `push` vers `main`, `master` et `clean-main`
- `pull_request`

Le job de deploiement Render reste limite a la branche `main`.

## Deploiement

Le projet est prepare pour plusieurs modes d'execution :

- [Dockerfile](/d:/Projet estate/Dockerfile:1) : image full-stack qui build le frontend puis le sert via FastAPI
- [docker-compose.yml](/d:/Projet estate/docker-compose.yml:1) : execution separee backend/frontend en local
- [render.yaml](/d:/Projet estate/render.yaml:1) : configuration d'un service Docker Render

En production, FastAPI expose l'API et sert le frontend compile si `frontend/dist` est present.

## Documentation complementaire

- [RAPPORT_GENERAL.md](/d:/Projet estate/RAPPORT_GENERAL.md:1)
- [docs/architecture.md](/d:/Projet estate/docs/architecture.md:1)
- [docs/competencies_mapping.md](/d:/Projet estate/docs/competencies_mapping.md:1)
- [docs/continuous_delivery.md](/d:/Projet estate/docs/continuous_delivery.md:1)
- [docs/agile_project_management.md](/d:/Projet estate/docs/agile_project_management.md:1)

## Positionnement RNCP

Le projet a ete cadre prioritairement pour soutenir les blocs suivants :

- **E1** : collecte, stockage et mise a disposition des donnees
- **E3** : integration, exposition et fiabilisation du modele IA
- **E4** : conception, developpement, test et livraison de l'application
