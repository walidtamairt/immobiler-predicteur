# Pilotage Agile du projet

## Objet

Cette note documente la logique de pilotage du projet dans un cadre Agile.

L'objectif est de montrer que la realisation technique n'a pas ete menee comme un bloc unique, mais selon une progression iterative et priorisee.

## Besoin initial

Le projet repond a un besoin metier clair :

- comprendre le marche immobilier,
- estimer un bien,
- exploiter un modele IA dans une application concrete,
- fournir des indicateurs et un assistant contextualise.

## Logique de decoupage

Le projet a ete structure par blocs fonctionnels successifs.

### Phase 1 - Data foundation

- analyse du dataset,
- selection des variables utiles,
- nettoyage,
- creation de `property_age`,
- generation des jeux nettoyes.

### Phase 2 - Base cloud et persistence

- modelisation des tables,
- chargement dans Neon,
- verification des acces backend / ML / dashboards.

### Phase 3 - Industrialisation du modele

- entrainement XGBoost,
- evaluation,
- versioning,
- predictions batch,
- stockage des metriques.

### Phase 4 - Mise en application

- creation de l'API FastAPI,
- ajout des endpoints data et prediction,
- integration React des pages `Marche`, `Prediction` et `Assistant IA`.

### Phase 5 - Qualite et soutenance

- ajout de tests automatises,
- mise en place de la CI,
- documentation,
- raffinement de l'UX,
- preparation du deploiement.

## Methode de travail

La methode appliquee est une logique Agile simple :

- priorisation des blocs a plus forte valeur,
- validation a la fin de chaque etape,
- corrections progressives,
- integration continue des briques plutot qu'une livraison finale unique.

## Exemples de increments visibles

- d'abord le pipeline ETL,
- puis le chargement cloud,
- puis le modele,
- puis l'API,
- puis le frontend,
- puis le monitoring,
- puis les tests et la documentation.

## Outils et supports mobilises

- Git pour le versioning,
- GitHub Actions pour la verification continue,
- fichiers markdown de documentation pour garder une trace exploitable,
- Docker et Render pour la projection de delivery.

## Valeur de cette approche pour le projet

Cette organisation apporte :

- une progression lisible,
- une limitation des risques,
- une meilleure capacite a tester chaque brique,
- une documentation plus simple a relier aux competences RNCP.

## Conclusion

Le projet peut etre defendu comme une realisation Agile car il a ete :

- decoupe en blocs,
- livre de facon iterative,
- valide regulierement,
- documente tout au long de sa progression.

Cette demarche est particulierement utile pour soutenir E4, car elle montre une coordination technique et une progression maitrisee du produit.
