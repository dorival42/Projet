# Projet d'Informatique Avancé: HomeFlix, un système de recommendation de films

##  KOUMBA BOUNDA Louis-Marie <br> LECLERC Cédric <br>DORIVAL Pierre-Chrislin

## Sommaire
- [Contexte du projet](#contexte-du-projet)
- [Description du projet](#description-du-projet)
- [Création de la base de données](#création)
- [L'Application](#lapplication)



### Contexte du projet:
Le but projet a été de concevoir HomeFlix, une plateforme de recommandation de films offrant à chaque utilisateur ou utilisatrice une expérience personnalisée. Le système propose des listes de films adaptées aux goûts et préférences de chacun(e). Et pour cela, nous avons suivi un plan et nous avons utilisé les notions vu au cours de cours, nous permettant ainsi de répondre à la problématique.

### Description du projet

Le système de recommandation est composé de 3 services distincts qui communiquent entre eux :

1. **Base de données centrale (DuckDB)**  
   - Stocke les données des films (extraites de l'API TMDB et du dataset Kaggle).
   - Retient les évaluations (notes attribuées par les utilisateurs aux films).
   - Stocke les prédictions générées pour les recommandations futures.

2. **Backend (API REST)**  
   - Fournit une **API REST** permettant :
	   - De récupérer des recommandations pour un utilisateur donné.
	   - D'interroger les films disponibles dans la base.
   - Implémente un **modèle de filtrage collaboratif** (basé sur la factorisation matricielle SVD ou autre technique).

3. **Frontend (Dashboard)**  
   - Fournit un outil visuel pour :
     - Analyser les données des films : distribution des notes, évolution de la popularité des films.
     - Afficher les recommandations générées par l'API backend pour un utilisateur spécifique.

L'ensemble du système a été orchestré à l'aide de **Docker Compose**. 

### Création 

Dans un premier temps, il est tout à fait possible de créer une base de données en local sans devoir utilisé celle déja présente. Voici les différentes étapes :

1. **Récuperer le projet**
    De la manière que vous voulez créer un répértoire en local et récupérer les fichiers (en faisant par exemple un git clone). Vous pouvez bien sûr travailler avec la base de données déja présente et dans ce cas-là vous pouvez passer directement à la partie 3.

2. **Création d'une base de données**
    - Configuration de l'environnement de développement : <br>
    Tout d'abord, on vous conseille de créer un environnement virtuel, voici deux approches :
        - Approche 1 : Initialisation de l'environnement virtuelle
            Afin d'initialiser l'environnement de développement, à la racine du projet écrire.<br>
            **Sur Linux :** <br>
                `python3 -m venv .venv` <br>
                `Source .venv/bin/activate` <br>

            **Sur windows:** <br>
                `python -m venv .venv`  <br>
                `.venv/Scripts/activate` <br>

            **Installation des dépendances :** <br>
                `pip install -r requirements.txt`

        - Approche 2 (plus rapide) : <br>
            `pip install uv` ou `pip3 install uv` <br>
            `uv init` (uv initialise un environnement virtuelle à notre place) <br>
            `uv add -r requirments.txt` (uv est plus rapide que pip pour installer les dépendances)
    
    - Collecte des données depuis l'api : <br>
    Dans cette étape, vous allez récolter les données depuis l'api **TMBD**. 
    Pour ce faire, créez un fichier .env à la racine du projet pour mettre votre clé api , ou ici le **TMDB_BEARER_TOKEN** récolter sur TMDB, et sauvegarder le fichier. <br>
    *(Vous pouver récupérer votre clé api et votre token sur [TMBD](developer.themoviedb.org) )*

    Une fois tout cela prêt, il vous suffira de lancer le script présent à `backend/app/utils/data_from_api.py`.
    Puis de faire la même chose avec `backend/app/utils/database_loading`, votre base de données sera bien crée sous le nom de `film_reco.db`

    - Information : Un fichier jupt.ipynb est présent dans le dossier data pour s'approprier la base de donnée et faire quelques requête dessus si besoin *(il y a par exemple une instruction pour supprimer les films dans la table avec une release_date vide. Et normalement cela n'est pas sensé arrivé vu la construction de la table avec sqlalchemy mais si vous avez ce problème allez voir s'il y à des films avec une release_date vide)*.

### L'Application

1. **Accès à l'API**<br>
    Vous pouvez décider d'accéder à l'API pour tester les endpoints par exemple. Pour cela il vous suffit de faire `uvicorn backend.main:app --port 8000 --reload` (*--reload permet de relancer automatiquement le serveur unicorn en cas de changement dans le code*). <br>

    À partir de là, il vous suffit d'aller à l'adresse suivante:  [FastApi](http://127.0.0.1:8000/docs) et vous pourrer tester les endpoints.

2. **L'application**<br>
    Pour lancer l'application il suffit de faire
    ```bash
    docker-compose up --build
    ```
Maintenant à vous de jouer !
    


