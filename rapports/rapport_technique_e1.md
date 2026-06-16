# RAPPORT TECHNIQUE ÉPREUVE E1 — COLLECTE, STOCKAGE ET MISE À DISPOSITION DES DONNÉES
## Candidat : Walid Tamairt | Certification : Développeur en Intelligence Artificielle (RNCP37827)

## 1. CONTEXTE DU PROJET ET ALIGNEMENT MÉTIER

### 1.1 Problématique métier

Estate AI est une plateforme full-stack orientée immobilier qui transforme un dataset de type Ames Housing en service de valorisation, d’analyse et de prédiction du marché immobilier. Le cœur de la valeur du projet repose sur la donnée : la qualité des traitements d’extraction, de nettoyage, de stockage et de mise à disposition conditionne directement la pertinence des KPI affichés, la fiabilité des prédictions, la qualité des synthèses métiers et la robustesse du système d’aide à la décision.

Le projet exploite en premier lieu les fichiers [data/train.csv](</d:/Projet estate/data/train.csv>) et [data/test.csv](</d:/Projet estate/data/test.csv>), puis les enrichit avec deux couches de contexte externe. La première provient de l’API FRED dans [backend/etl/fetch_external_context.py](</d:/Projet estate/backend/etl/fetch_external_context.py:1>), qui récupère des indicateurs macroéconomiques liés au marché du logement américain. La seconde est produite par [backend/etl/scrape_market_trends.py](</d:/Projet estate/backend/etl/scrape_market_trends.py:1>), qui extrait ou simule des tendances de marché à partir de pages HTML. Enfin, la chaîne analytique locale s’appuie sur [backend/etl/big_data_duckdb.py](</d:/Projet estate/backend/etl/big_data_duckdb.py:1>) pour convertir les données en Parquet et produire une agrégation SQL rapide à l’aide de DuckDB.

La donnée gouverne donc le projet à trois niveaux :

- elle alimente le stockage relationnel ;
- elle sert à produire les analyses visibles dans le dashboard ;
- elle sert à entraîner le modèle XGBoost et à historiser les prédictions.

Le projet n’est pas un simple exercice de lecture CSV. C’est une chaîne de valeur data complète, depuis la collecte jusqu’à la restitution via API et interface web.

### 1.2 Architecture globale du système de données

Le flux réel de la donnée dans le projet peut être représenté ainsi :

```text
Fichiers sources locaux
  -> data/train.csv
  -> data/test.csv
         |
         v
backend/etl/ingest_data.py
  -> résolution de chemin
  -> lecture pandas
         |
         v
backend/etl/clean_data.py
  -> standardisation des colonnes
  -> sélection métier
  -> feature engineering
  -> imputation
  -> suppression des outliers
  -> export CSV propre
  -> export Parquet lake raw/processed
         |
         +------------------------------+
         |                              |
         v                              v
backend/etl/load_to_neon.py      backend/etl/big_data_duckdb.py
  -> chargement SQL                  -> conversion CSV -> Parquet
  -> Neon / SQLite                   -> agrégation analytique DuckDB
  -> tables métiers                  -> artefacts lake analytics
         |                              |
         +--------------+---------------+
                        v
            backend/app/api.py
  -> filtres
  -> dashboards
  -> historique
  -> métriques modèle
  -> prédiction unitaire
  -> assistant IA
                        |
                        v
                frontend React
  -> marché
  -> prediction
  -> assistant IA
```

Cette architecture montre une séparation nette entre :

- la couche d’ingestion et de préparation ;
- la couche de persistance ;
- la couche analytique ;
- la couche de service REST ;
- la couche de restitution utilisateur.

### 1.3 Stack technologique justifiée

Le choix de Python est cohérent avec l’ensemble des traitements du projet. Il permet de centraliser l’ingestion, la préparation, l’agrégation, l’API et l’intégration du modèle machine learning dans un même langage de production.

FastAPI est utilisé dans [backend/app/main.py](</d:/Projet estate/backend/app/main.py:1>) et [backend/app/api.py](</d:/Projet estate/backend/app/api.py:1>) parce qu’il fournit :

- un routeur REST lisible et modulaire ;
- une validation des dépendances par injection ;
- une génération automatique d’OpenAPI/Swagger ;
- une compatibilité directe avec les mécanismes d’authentification standard ;
- un très bon compromis entre simplicité et robustesse pour un projet RNCP.

PostgreSQL, porté par Neon en production, constitue la base relationnelle de référence. La configuration de session et d’engine est centralisée dans [backend/app/database.py](</d:/Projet estate/backend/app/database.py:1>) et les tables sont décrites dans [backend/database/schema.sql](</d:/Projet estate/backend/database/schema.sql:1>). Le projet supporte aussi SQLite pour les tests et le mode local, ce qui permet de valider le pipeline sans dépendre d’un service cloud actif.

DuckDB est intégré comme brique analytique locale dans [backend/etl/big_data_duckdb.py](</d:/Projet estate/backend/etl/big_data_duckdb.py:1>). Ce choix est pertinent car DuckDB est :

- colonne-orienté pour l’analytique ;
- rapide sur les fichiers Parquet ;
- simple à exécuter localement ;
- adapté aux requêtes SQL de type analytique ;
- excellent pour simuler un traitement de volumes massifs sans infrastructure distribuée.

Pytest enfin est utilisé pour prouver la stabilité du code. La suite de tests [backend/tests](</d:/Projet estate/backend/tests>) couvre les endpoints, l’ETL, l’entrainement, le monitoring et le scraping, ce qui renforce la crédibilité du projet dans un contexte de certification.

## 2. COMPÉTENCE C1 : AUTOMATISATION ET EXTRACTION MULTI-SOURCES

### 2.1 Extraction multi-sources

La compétence C1 demande une automatisation de l’extraction depuis plusieurs sources. Le projet la couvre de manière concrète avec trois familles de sources : fichier local, API externe et scraping HTML.

#### Extraction depuis les fichiers locaux

Le point d’entrée est [backend/etl/ingest_data.py](</d:/Projet estate/backend/etl/ingest_data.py:1>). Ce module :

- résout le chemin du fichier demandé ;
- accepte un chemin explicite ou un fallback vers `data/<nom_du_fichier>` ;
- lit le CSV avec pandas ;
- gère proprement les erreurs de lecture ;
- valide la présence des colonnes nécessaires au train.

Le mécanisme de fallback est important : il permet au projet de fonctionner aussi bien avec les chemins documentés qu’avec les chemins réellement présents dans le dépôt. C’est une forme simple mais utile de robustesse d’ingestion.

L’extraction locale est ensuite exploitée par [backend/etl/clean_data.py](</d:/Projet estate/backend/etl/clean_data.py:1>), qui consomme les deux CSV source :

- `data/train.csv`
- `data/test.csv`

Le nettoyage produit ensuite :

- `data/processed/train_clean.csv`
- `data/processed/test_clean.csv`
- `data/lake/raw/train_raw.parquet.gzip`
- `data/lake/raw/test_raw.parquet.gzip`
- `data/lake/processed/train_clean.parquet.gzip`
- `data/lake/processed/test_clean.parquet.gzip`

Le projet couvre donc bien l’extraction à partir de fichiers de données, puis leur préparation pour la suite du flux.

#### Extraction depuis un service web / API externe

La collecte web externe est réalisée dans [backend/etl/fetch_external_context.py](</d:/Projet estate/backend/etl/fetch_external_context.py:1>). Le script :

- lit la variable d’environnement `FRED_API_KEY` ;
- interroge l’API FRED ;
- tente plusieurs séries dans l’ordre ;
- garde la première série exploitable ;
- transforme la réponse JSON en DataFrame ;
- produit un CSV et un JSON de synthèse ;
- charge ces résultats en base si possible.

Les séries ciblées sont :

- `MORTGAGE30US`
- `CPIAUCSL`
- `UNRATE`

Cette logique montre une vraie automatisation d’extraction depuis un service web via HTTP, avec gestion des erreurs réseau, des réponses invalides et des cas de repli.

Le fichier de sortie principal est [data/external/external_market_context.csv](</d:/Projet estate/data/external/external_market_context.csv>) et le résumé associé est [data/external/external_market_summary.json](</d:/Projet estate/data/external/external_market_summary.json>). Le script ne se contente pas de télécharger des données : il les reformate et les rend réutilisables par l’API et le dashboard.

#### Extraction par scraping ou pseudo-scraping

Le scraping est géré dans [backend/etl/scrape_market_trends.py](</d:/Projet estate/backend/etl/scrape_market_trends.py:1>). Le script peut fonctionner de trois manières :

- à partir d’un HTML local ;
- à partir d’une URL distante ;
- à partir d’une recherche web DuckDuckGo HTML.

Le script sait :

- charger un document HTML ;
- télécharger une page distante ;
- récupérer des résultats de recherche ;
- parser des cartes `.market-trend` ;
- parser un tableau de style Numbeo ;
- parser un tableau HTML générique ;
- produire des enregistrements homogènes ;
- générer un CSV et un JSON de synthèse ;
- charger ces sorties en base.

Le mock HTML [data/external/mock_market_trends.html](</d:/Projet estate/data/external/mock_market_trends.html>) permet de démontrer la logique même sans dépendre d’un site externe instable.

Le résultat du scraping est exploité dans :

- [data/external/scraped_market_trends.csv](</d:/Projet estate/data/external/scraped_market_trends.csv>)
- [data/external/scraped_market_trends_summary.json](</d:/Projet estate/data/external/scraped_market_trends_summary.json>)

Cette brique répond clairement à l’idée d’un scraping automatisé et d’une extraction de tendance de marché exploitable en production légère ou en démonstration RNCP.

### 2.2 Ingestion analytique et justification "Big Data"

Le script [backend/etl/big_data_duckdb.py](</d:/Projet estate/backend/etl/big_data_duckdb.py:1>) apporte la composante analytique attendue pour C1. Sa logique est la suivante :

1. convertir les CSV bruts en Parquet ;
2. exécuter une agrégation SQL analytique sur les Parquet ;
3. persister les résultats pour réutilisation.

Le script utilise DuckDB avec un traitement vectorisé local. Ce point est important pour le référentiel : il ne s’agit pas seulement d’un SQL sur un petit fichier, mais d’un moteur analytique conçu pour lire efficacement des données colonnes, exécuter des agrégations complexes et produire un résultat exploitable sans passer par un cluster distribué.

Concrètement, `run_big_data_pipeline()` :

- convertit `data/train.csv` en `data/lake/raw/train_bigdata.parquet` ;
- convertit `data/test.csv` en `data/lake/raw/test_bigdata.parquet` ;
- calcule une agrégation analytique sur le train ;
- produit `data/lake/analytics/neighborhood_month_metrics.csv` ;
- produit `data/lake/analytics/neighborhood_month_metrics.parquet.gzip`.

La requête DuckDB exploite :

- `read_csv_auto()`
- `read_parquet()`
- `GROUP BY`
- `AVG()`
- `MEDIAN()`
- `COUNT()`
- `DENSE_RANK() OVER (...)`
- un tri final des segments

Le résultat est une table analytique par quartier, style de maison et mois de vente, avec :

- le nombre de biens ;
- le prix moyen ;
- la médiane ;
- la surface moyenne ;
- le prix moyen au pied carré ;
- le rang du segment dans le mois.

Cette brique est particulièrement utile pour la validation C1 car elle démontre un traitement local de type data analytics à fort volume potentiel :

- les données sont converties dans un format colonnes optimisé ;
- la logique SQL est pensée pour l’agrégation ;
- le pipeline est reproductible ;
- la sortie est directement exploitable par d’autres couches du projet.

Le fait que le projet stocke aussi ces résultats dans `data/lake/analytics/` renforce la traçabilité du traitement et la séparation entre données brutes, données préparées et données analytiques.

## 3. COMPÉTENCE C2 : DÉVELOPPEMENT DES REQUÊTES SQL D’EXTRACTION ET D’AGRÉGATION

### 3.1 Modélisation et persistance

Le schéma relationnel principal du projet est défini dans [backend/database/schema.sql](</d:/Projet estate/backend/database/schema.sql:1>). Il contient les tables suivantes :

- `properties_train`
- `model_metrics`
- `batch_predictions`
- `user_predictions`
- `external_market_context`
- `scraped_market_trends`
- `external_context_summaries`

Cette modélisation est cohérente avec l’usage métier :

- `properties_train` contient le cœur de la donnée de marché ;
- `model_metrics` stocke les métriques de chaque entraînement ;
- `batch_predictions` permet la prédiction de masse ;
- `user_predictions` journalise les estimations réalisées par l’utilisateur ;
- `external_market_context` conserve les indicateurs macroéconomiques ;
- `scraped_market_trends` conserve les tendances extraites du web ;
- `external_context_summaries` conserve les résumés textuels des enrichissements.

La persistance est mise en œuvre via SQLAlchemy dans [backend/app/database.py](</d:/Projet estate/backend/app/database.py:1>) et via les classes ORM de [backend/app/models.py](</d:/Projet estate/backend/app/models.py:1>). Chaque table est structurée autour d’une clé primaire `id`, avec des colonnes typées pour les données immobilières, les séries temporelles et les métadonnées.

Dans le code ORM, les champs `id` sont déclarés avec `index=True`. Dans le SQL physique, la clé primaire est `SERIAL PRIMARY KEY`. Cela signifie que le projet bénéficie d’indexation sur les identifiants et de performances correctes pour :

- les accès aux derniers enregistrements ;
- les historiques courts ;
- les chargements par lots ;
- les tris temporels.

Le projet ne définit pas de grands index secondaires spécialisés sur les colonnes métiers, ce qui est cohérent avec un MVP simple et des volumes maîtrisés. L’optimisation est plutôt assurée par :

- la sélection d’un sous-ensemble de données ;
- l’usage de `limit()` ;
- les agrégations ciblées ;
- la simplicité du schéma ;
- le stockage séparé des cas d’usage.

### 3.2 Requêtes complexes et performances

Les requêtes d’extraction et d’agrégation métier sont portées par [backend/app/api.py](</d:/Projet estate/backend/app/api.py:1>). Elles s’appuient sur SQLAlchemy et sur la base relationnelle pour éviter de recalculer les agrégats côté frontend.

Les endpoints les plus structurants sont :

- `GET /api/market-dashboard`
- `GET /api/overview`
- `GET /api/filters`
- `GET /api/price-analysis`
- `GET /api/location-analysis`
- `GET /api/batch-predictions`
- `GET /api/prediction-history`
- `GET /api/model-metrics/latest`
- `GET /api/model-metrics/history`
- `GET /api/market-data`

Le endpoint `/api/market-dashboard` est le plus riche. Il :

- applique un filtrage croisé sur `neighborhood`, `house_style`, `overall_qual`, `bedroom_abv_gr`, `full_bath`, `sale_month`, `property_age_min`, `property_age_max` ;
- calcule les KPI globaux ;
- agrège par quartier ;
- agrège par qualité ;
- agrège par mois ;
- produit une distribution des prix ;
- construit un nuage de points prix/surface ;
- produit une synthèse métier.

Le filtrage croisé est entièrement piloté côté backend via `build_filtered_query()`. Les clauses `filter()` sont chaînées sur `PropertyTrain`, ce qui garde la logique simple et lisible. Les agrégations sont faites avec `func.avg`, `func.count`, `func.min`, `func.max`, `group_by`, `having` et `order_by`.

Le endpoint `/api/overview` illustre une autre forme de lecture analytique :

- moyenne des prix ;
- prix moyen au m² ou au pied carré ;
- total de biens ;
- surface moyenne.

Le endpoint `/api/filters` sert à alimenter le frontend avec les valeurs distinctes disponibles dans la base, ce qui évite de coder les listes à la main dans l’interface.

Le endpoint `/api/model-metrics/history` fournit un historique ordonné des métriques du modèle, et `/api/batch-predictions` expose les résultats d’inférence batch. Ces endpoints montrent que la donnée n’est pas seulement consommée une fois : elle est structurée pour plusieurs usages.

Concernant l’indexation, le code montre une optimisation raisonnable pour le niveau du projet :

- index sur les clés primaires ;
- chargement limité aux derniers enregistrements pour les historiques ;
- agrégations directes côté base ;
- suppression du sur-traitement côté UI ;
- calculs les plus coûteux réalisés une seule fois par requête API.

## 4. COMPÉTENCE C3 : DÉVELOPPEMENT DES RÈGLES D’AGRÉGATION ET NETTOYAGE (ETL)

### 4.1 Pipeline de nettoyage

Le nettoyage est encapsulé dans [backend/etl/clean_data.py](</d:/Projet estate/backend/etl/clean_data.py:1>). Ce script constitue la véritable colonne vertébrale de la qualité de la donnée dans Estate AI.

Le pipeline suit l’ordre logique suivant :

1. standardiser les noms de colonnes ;
2. sélectionner uniquement les colonnes utiles ;
3. créer la variable dérivée `property_age` ;
4. imputer les valeurs manquantes ;
5. supprimer les doublons ;
6. retirer les outliers ;
7. finaliser l’ordre des colonnes ;
8. réindexer ;
9. exporter les résultats.

#### Traitement des valeurs manquantes et imputation

Les colonnes catégorielles :

- `Neighborhood`
- `HouseStyle`

sont remplies avec `Unknown` quand elles sont absentes.

Les colonnes numériques sont converties avec `pd.to_numeric(..., errors="coerce")`, puis complétées avec la médiane de la colonne. Si la médiane est indéfinie, le code retombe sur `0`.

Cette logique est cohérente avec un pipeline robustement défini :

- elle évite les ruptures de type ;
- elle conserve une valeur centrale réaliste ;
- elle limite l’impact des valeurs aberrantes sur l’imputation.

#### Détection et suppression des outliers

Le script supprime plusieurs formes de valeurs extrêmes :

- suppression des doublons ;
- filtrage des biens de surface habitable supérieure ou égale à `3000` ;
- filtrage des `LotArea` au-dessus du quantile `0.995` ;
- sur le train, filtrage des prix en dehors de la plage `[10000, 1000000]`.

Ces règles évitent d’introduire dans le modèle des cas trop atypiques qui pourraient distordre les distributions ou dégrader les performances.

#### Feature engineering

La colonne la plus importante créée par le script est `property_age`, calculée à partir de `YearBuilt` et d’une année de référence `2010`. Le projet ne se contente donc pas de nettoyer : il enrichit les données avec une variable interprétable métier qui aide ensuite le modèle et les analyses.

Le feature engineering est volontairement simple, ce qui est un bon choix pour un projet RNCP :

- il est lisible ;
- il est reproductible ;
- il est défendable ;
- il est utile au modèle ;
- il peut être expliqué facilement en soutenance.

#### Exportation des données propres

Le script exporte à la fois :

- des CSV propres dans `data/processed/` ;
- des snapshots Parquet dans `data/lake/raw/` et `data/lake/processed/`.

Le `data lake` local sert ici à conserver les différentes couches de préparation, ce qui améliore la traçabilité. Les sorties sont exploitables directement par :

- [backend/etl/load_to_neon.py](</d:/Projet estate/backend/etl/load_to_neon.py:1>) ;
- [backend/ml/train_model.py](</d:/Projet estate/backend/ml/train_model.py:1>) ;
- [backend/ml/predict_batch.py](</d:/Projet estate/backend/ml/predict_batch.py:1>) ;
- [backend/etl/big_data_duckdb.py](</d:/Projet estate/backend/etl/big_data_duckdb.py:1>).

## 5. COMPÉTENCE C4 : CONFORMITÉ RGPD ET BASE DE DONNÉES

### 5.1 Principes du RGPD appliqués au code

Le projet est naturellement sobre sur le plan RGPD car il manipule essentiellement des attributs de biens immobiliers et non des données personnelles.

Dans le périmètre réellement exploité par le code :

- aucun nom ;
- aucune adresse email utilisateur ;
- aucun numéro de téléphone ;
- aucun identifiant direct de personne physique ;
- aucun profil nominatif.

Les données persistées dans les tables métier sont :

- des caractéristiques de biens ;
- des indicateurs macroéconomiques ;
- des tendances de marché ;
- des métriques de modèle ;
- des prédictions et historiques de prédiction.

Cela permet de défendre un principe de minimisation :

- seules les variables utiles au projet sont conservées ;
- le train a été réduit à un sous-ensemble de colonnes métier ;
- les données externes sont agrégées et synthétisées ;
- la journalisation métier n’enregistre pas de donnée personnelle dans l’état actuel du code.

Le code ne définit pas de mécanisme de chiffrement des identifiants utilisateurs car il n’y a pas de compte utilisateur métier dans la version actuelle. L’authentification ajoutée dans [backend/app/auth.py](</d:/Projet estate/backend/app/auth.py:1>) protège l’accès aux endpoints sensibles par clé API, mais elle ne crée pas de base de données d’utilisateurs.

Concernant la conservation et la purge, le projet gère plusieurs formes de données temporaires :

- les artefacts de lake ;
- les fichiers de sortie ETL ;
- les snapshots de monitoring ;
- les historiques de batch et de prédiction.

Les scripts d’ingestion et de chargement réécrivent certaines tables lors d’un nouveau cycle, ce qui joue un rôle de purge technique sur les tables de staging et les jeux reconstruits. En revanche, le code ne met pas en place de politique RGPD de rétention fine pour des logs applicatifs persistants, car ce n’est pas un besoin fonctionnel du MVP actuel. C’est un point qui peut être présenté honnêtement en soutenance : le projet est conforme par minimisation sur son périmètre de données, mais il ne constitue pas un système de gestion d’identité ou de journal d’audit réglementaire avancé.

## 6. COMPÉTENCE C5 : API REST DE MISE À DISPOSITION SÉCURISÉE DES DONNÉES

### 6.1 Architecture de l’API FastAPI

L’API est définie dans [backend/app/api.py](</d:/Projet estate/backend/app/api.py:1>) et montée dans [backend/app/main.py](</d:/Projet estate/backend/app/main.py:1>).

FastAPI sert ici à exposer les données de marché et les résultats du modèle sous forme REST. Les endpoints disponibles couvrent :

- la santé de l’application ;
- le marché brut ;
- le dashboard marché ;
- les filtres ;
- les analyses par quartier et qualité ;
- les analyses de localisation ;
- les historiques de prédictions ;
- les métriques de modèle ;
- la prédiction unitaire ;
- le chat assistant.

Le routeur est préfixé par `/api`. L’interface React consomme ensuite cette API dans [frontend/src/services/api.js](</d:/Projet estate/frontend/src/services/api.js:1>).

L’API joue donc bien son rôle de couche de mise à disposition, conformément à C5.

### 6.2 Sécurisation et authentification

La sécurisation par clé API est implémentée dans [backend/app/auth.py](</d:/Projet estate/backend/app/auth.py:1>).

Le module introduit :

- un header `X-API-Key` via `APIKeyHeader` ;
- une dépendance `require_api_key()` ;
- un objet léger `AuthenticatedPrincipal` ;
- un schéma d’authentification exposé dans OpenAPI sous `ApiKeyAuth`.

Le mécanisme fonctionne avec FastAPI de manière idiomatique :

- la sécurité est injectée via `Security(require_api_key)` ;
- les routes sensibles sont protégées sans modifier leur logique métier ;
- l’erreur renvoyée en cas d’accès refusé est un `401 Unauthorized`.

Dans l’état actuel du code, les routes protégées sont :

- `GET /api/market-data`
- `GET /api/batch-predictions`
- `GET /api/prediction-history`
- `POST /api/predict`

Cela protège les points sensibles qui exposent l’intégralité des données métier, les historiques et l’inférence.

La clé utilisée est configurée dans [backend/config/settings.py](</d:/Projet estate/backend/config/settings.py:1>) avec une valeur par défaut de développement `estate-ai-dev-key`, surchargée en production par variable d’environnement. Cette approche est simple, lisible et suffisante pour une certification où l’objectif est de montrer une authentification effective, pas forcément une solution IAM complète.

### 6.3 Auto-documentation

FastAPI génère automatiquement la documentation OpenAPI. L’utilisation de `APIKeyHeader` et de `Security(...)` enrichit cette documentation avec le schéma `ApiKeyAuth`.

Le résultat est visible dans :

- Swagger UI ;
- les schémas OpenAPI produits par l’application ;
- la déclaration automatique du besoin de clé API pour les routes sécurisées.

Ce point est important pour l’accessibilité technique : la documentation n’est pas un document séparé, mais une propriété du service lui-même. Cela facilite la prise en main par un développeur, un évaluateur ou un intégrateur.

## Synthèse technique des preuves de code

Les principaux fichiers de preuve pour l’épreuve E1 sont :

- [backend/etl/ingest_data.py](</d:/Projet estate/backend/etl/ingest_data.py:1>)
- [backend/etl/clean_data.py](</d:/Projet estate/backend/etl/clean_data.py:1>)
- [backend/etl/load_to_neon.py](</d:/Projet estate/backend/etl/load_to_neon.py:1>)
- [backend/etl/fetch_external_context.py](</d:/Projet estate/backend/etl/fetch_external_context.py:1>)
- [backend/etl/scrape_market_trends.py](</d:/Projet estate/backend/etl/scrape_market_trends.py:1>)
- [backend/etl/big_data_duckdb.py](</d:/Projet estate/backend/etl/big_data_duckdb.py:1>)
- [backend/database/schema.sql](</d:/Projet estate/backend/database/schema.sql:1>)
- [backend/app/api.py](</d:/Projet estate/backend/app/api.py:1>)
- [backend/app/auth.py](</d:/Projet estate/backend/app/auth.py:1>)
- [backend/app/database.py](</d:/Projet estate/backend/app/database.py:1>)
- [backend/app/models.py](</d:/Projet estate/backend/app/models.py:1>)
- [backend/tests](</d:/Projet estate/backend/tests>)
- [backend/requirements.txt](</d:/Projet estate/backend/requirements.txt:1>)

## Conclusion opérationnelle

Le projet Estate AI répond de manière cohérente aux attentes du bloc E1 du référentiel RNCP37827. Il démontre :

- une collecte automatisée multi-sources ;
- un nettoyage et une homogénéisation robustes ;
- une persistance relationnelle claire ;
- une brique analytique DuckDB/Parquet pertinente ;
- une API REST de mise à disposition ;
- une sécurisation par clé API sur les routes sensibles ;
- une documentation OpenAPI automatique ;
- une base de tests qui valide la stabilité du flux.

Le rapport peut donc servir de support technique de soutenance pour l’épreuve E1, à condition de présenter honnêtement le cadre du projet : une simulation analytique locale très solide, articulée autour d’un vrai pipeline data, mais sans infrastructure big data distribuée. Cette précision ne diminue pas la valeur du travail ; elle le rend au contraire plus crédible.
