# Model Strategy

## Features

Le modele est volontairement simple et exploitable:

Numeriques:

- `GrLivArea`
- `LotArea`
- `OverallQual`
- `OverallCond`
- `BedroomAbvGr`
- `FullBath`
- `GarageCars`
- `GarageArea`
- `MoSold`
- `property_age`

Categorielle:

- `Neighborhood`
- `HouseStyle`

Target:

- `SalePrice`

## Entrainement

Le pipeline utilise:

- `ColumnTransformer`,
- `SimpleImputer`,
- `OneHotEncoder(handle_unknown="ignore")`,
- `XGBRegressor`.

Le split train/validation est fait avec `train_test_split(random_state=42)` pour garder un comportement reproductible.

## Evaluation

Les metriques calculees sont:

- `MAE`
- `RMSE`
- `R2`

Elles sont enregistrees dans `model_metrics` avec le nombre de lignes et le nombre de features.

## Stockage des predictions

Les predictions batch sont stockees dans `batch_predictions` avec:

- les features utiles,
- `predicted_price`,
- `model_version`,
- un identifiant source optionnel.

Cela permet de reutiliser les predictions pour les dashboards, l API et une logique future de type smart deal.
