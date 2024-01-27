# Projet final 5MLDE 

## Prérequis 

TODO : guide installation docker

## Lancer le projet

Lancer les commandes suivantes :
````shell
git clone https://github.com/baptdav/5MLDE_PROJ
cd infra
docker compose up
````

Puis attendre ~2 minutes que tout s'execute.

## Tests Great Expectations

TODO : 

## Workflow Prefect

TODO : Expliquer brièvement notre workflow (en montrant la partition d'execution de ce dernier?) et en expliquant le rôle de chacun des subflows 

## Déploiements MLFlow

### Expériences

TODO : Dire ce qu'on log (Modèle + préprocesseur + résultats tests great expectatiob + métriques) (avec des captures ?)

### Modèles enregistrés

TODO : Dire les modèles qu'on enregistre et pq (modèle + préprocesseur) + expliquer système d'alias et de tag pour montrer les release (également préciser la dif entre un modèle en prod et pas en prod : on prend la dernière version en prod pour faire les predictions de notre API)

## Liens utiles 

- MLFLOW : 
  - Experiments : http://localhost:5000/#/experiments/
  - Models : http://localhost:5000/#/models
- PREFECT : http://localhost:4200/
    - Dashboard : http://localhost:4200/dashboard
    - Deployments : http://localhost:4200/deployments
    - Flows : http://localhost:4200/flows
    - Flow runs : http://localhost:4200/flow-runs
- API PREDICT : http://localhost:5001/predict

## Exemple de requête pour appeler l'API du modèle : 

````shell
curl --location 'http://localhost:5001/predict' \
--header 'Content-Type: application/json' \
--data '{
    "age": 56,
    "job": "housemaid",
    "marital": "married",
    "education": "basic.4y",
    "default": "no",
    "housing": "no",
    "loan": "no",
    "contact": "telephone",
    "month": "may",
    "day_of_week": "mon",
    "duration": 261,
    "campaign": 1,
    "pdays": 999,
    "previous": 0,
    "poutcome": "nonexistent",
    "emp.var.rate": 1.1,
    "cons.price.idx": 93.994,
    "cons.conf.idx": -36.4,
    "euribor3m": 4.857,
    "nr.employed": 5191
}'
````