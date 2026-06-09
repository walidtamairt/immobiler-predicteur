# Data Strategy

Le dataset Ames Housing contient trop de colonnes pour un MVP cloud. L objectif est de garder un sous-ensemble stable, lisible et utile pour la prediction et les dashboards.

## Colonnes supprimees

Les colonnes supprimees sont celles qui:

- apportent peu de signal pour un modele simple,
- sont trop bruitées ou trop redondantes,
- complexifient le schema et le frontend,
- augmentent inutilement le volume stocke en base.

Cela inclut notamment les champs de type detail architectural, commodites secondaires, ou variables très fragmentées.

## Colonnes conservees

Les variables conservees sont celles qui capturent le plus souvent:

- la taille du bien,
- la qualité,
- la composition,
- l anciennete,
- le contexte de quartier.

Le jeu final garde:

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
- `SalePrice` pour l entrainement uniquement

## Limitation du volume

Si un dataset dépasse `110000` lignes, il est echantillonne avec `random_state=42` pour rester reproductible et limiter la charge Neon.

## Pourquoi ce design

Ce design est meilleur pour Neon et le frontend parce qu il:

- reduit le stockage,
- accelere les requetes,
- simplifie les schemas SQL,
- rend les dashboards plus faciles a construire,
- facilite le deploiement et les relances de pipeline.
