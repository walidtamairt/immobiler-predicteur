# Livraison continue et packaging

## Objet

Cette documentation explique comment le projet assure aujourd'hui une logique de livraison continue dans un cadre de projet IA.

L'objectif n'est pas de presenter une chaine enterprise tres complexe, mais une chaine credible, reproductible et defendable pour le projet actuel.

## Principe general

La chaine de delivery repose sur trois idees simples :

1. versionner le code, les tests et les configurations,
2. executer automatiquement les verifications importantes,
3. produire un artefact de modele reutilisable.

## Workflow GitHub Actions

Le projet utilise :

- [.github/workflows/mlops-ci.yml](/d:/Projet estate/.github/workflows/mlops-ci.yml:1)

Cette chaine est declenchee sur :

- `push` sur `main` ou `master`,
- `pull_request`.

## Etapes automatisees actuellement

La pipeline execute :

1. checkout du depot,
2. installation de Python,
3. installation des dependances backend,
4. execution des tests automatises,
5. nettoyage des donnees,
6. entrainement du modele,
7. verification de la presence de l'artefact et du fichier de metriques.

## Ce que la chaine garantit

La chaine garantit que :

- le code backend est testable,
- les tests du projet passent avant validation,
- le pipeline data de base reste executable,
- l'entrainement du modele reste reproductible,
- les artefacts attendus sont bien generes.

## Artefacts verifies

La pipeline verifie explicitement l'existence de :

- `backend/ml/models/xgboost_model.joblib`
- `backend/ml/models/metrics.json`

Ces fichiers servent de preuve de bon fonctionnement de la partie modele.

## Place des tests automatises

La livraison continue s'appuie sur une base de tests versionnes dans :

- [backend/tests](/d:/Projet estate/backend/tests:1)

Ces tests couvrent principalement :

- l'API,
- le pipeline ETL,
- les contrats de donnees,
- l'entrainement du modele,
- les predictions batch.

## Packaging applicatif

Le projet est egalement prepare pour le packaging applicatif.

Fichiers disponibles :

- [backend/Dockerfile](/d:/Projet estate/backend/Dockerfile:1)
- [frontend/Dockerfile](/d:/Projet estate/frontend/Dockerfile:1)
- [docker-compose.yml](/d:/Projet estate/docker-compose.yml:1)

Ce packaging permet :

- une execution locale plus stable,
- une meilleure reproductibilite,
- une logique de pre-production simple a demonstrer.

## Deploiement cible

Le deploiement vise :

- **Neon PostgreSQL** pour la persistance cloud,
- **Render** pour le backend via Docker,
- **Render** pour le frontend via Docker.

La configuration Render est documentee dans :

- [render.yaml](/d:/Projet estate/render.yaml:1)

## Limites actuelles a presenter honnetement

Pour une soutenance, il est utile de dire clairement que :

- la chaine actuelle automatise surtout le backend et la partie ML,
- le frontend n'est pas encore teste dans la CI,
- le deploiement final sur Render est prepare mais peut rester manuel selon le contexte de soutenance.

Cette transparence renforce la credibilite du dossier.

## Conclusion

Le projet dispose d'une logique de livraison continue suffisamment solide pour etre defendue :

- tests automatises,
- entrainement reproductible,
- verification des artefacts,
- packaging prevu,
- cible de deploiement documentee.

Cela permet de montrer que le projet n'est pas seulement developpe, mais aussi **prepare pour une mise a disposition fiable**.
