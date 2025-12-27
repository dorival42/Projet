import requests
import os
import streamlit as st
from datetime import datetime

# Récupère l'URL du backend à partir des variables d'environnement, sinon utilise une URL par défaut
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# def get_all_movies(page: int = 1):
#     """
#     Récupère une liste paginée de films depuis l'API backend.

#     Args:
#         page (int): Numéro de page pour la pagination (par défaut 1).

#     Returns:
#         list: Liste des films disponibles pour la page spécifiée.
#     """
#     try:
#         resp = requests.get(f"{BACKEND_URL}/films?page={page}")
#         resp.raise_for_status()
#         data = resp.json()
#         return data.get("films", [])  # On extrait uniquement la liste de films
#     except Exception as e:
#         print(f"Erreur lors de get_all_movies: {e}")
#         return []

def get_all_movies():
    """
    Récupère tous les films depuis l'API backend, page par page.
    
    Returns:
        list: Liste de tous les films disponibles.
    """
    all_movies = []
    page = 1
    while True:
        try:
            # Récupérer les films de la page actuelle
            resp = requests.get(f"{BACKEND_URL}/films?page={page}")
            resp.raise_for_status()  # Vérifie si la requête a réussi
            data = resp.json()
            movies = data.get("films", [])
            
            if not movies:
                break  # Si aucune donnée n'est renvoyée, on arrête la boucle

            # Ajouter les films récupérés à la liste
            all_movies.extend(movies)
            page += 1  # Passer à la page suivante
            
        except Exception as e:
            print(f"Erreur lors de la récupération des films: {e}")
            st.write(page)
            break  # Si une erreur survient, arrêter la récupération des films
    
    return all_movies

def get_movie_by_id(movie_id: int):
    """
    Récupère les détails d’un film spécifique via son identifiant.

    Args:
        movie_id (int): Identifiant unique du film.

    Returns:
        dict | None: Dictionnaire contenant les informations du film, ou None si la requête échoue.
    """
    response = requests.get(f"{BACKEND_URL}/films/{movie_id}")
    return response.json() if response.status_code == 200 else None


def get_user_recommendations(user_id: int, num_recommendations: int = 5):
    """
    Récupère des recommandations de films personnalisées pour un utilisateur.

    Args:
        user_id (int): Identifiant unique de l'utilisateur.
        num_recommendations (int): Nombre de recommandations souhaitées (par défaut 5).

    Returns:
        list: Liste de recommandations de films ou liste vide si la requête échoue.
    """
    params = {"num_recommendations": num_recommendations}
    response = requests.post(f"{BACKEND_URL}/recommendation_movies/{user_id}", params=params)
    return response.json() if response.status_code == 200 else []


def get_statistics_by_genre_year(genre: str, year: int):
    """
    Récupère des statistiques de films en fonction du genre et de l'année.

    Args:
        genre (str): Genre du film (ex: "Action", "Comédie", etc.).
        year (int): Année de sortie.

    Returns:
        dict | None: Statistiques liées au genre et à l'année, ou None si la requête échoue.
    """
    response = requests.get(f"{BACKEND_URL}/statistics/{genre}/{year}")
    return response.json() if response.status_code == 200 else None


def afficher_film_complet(film_id: int):
    """
    Affiche les détails complets d'un film dans une interface Streamlit.

    Args:
        film_id (int): Identifiant du film à afficher.

    Effets de bord:
        Affiche les informations du film dans l'interface Streamlit.
    """
    film_data = get_movie_by_id(film_id)

    if not film_data:
        st.error("Film introuvable.")
        return

    # Extraction des données principales du film
    title = film_data.get("title")
    release_date = film_data.get("release_date")
    overview = film_data.get("description", "Aucune description disponible.")
    vote_average = film_data.get("vote_average")
    poster_path = film_data.get("poster_path")
    genres = film_data.get("genres", "")
    vote_count = film_data.get("vote_count")

    # Affichage en deux colonnes : image à gauche, infos à droite
    col1, col2 = st.columns([1, 2])

    with col1:
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            st.image(poster_url, width=300)

    with col2:
        st.title(title)
        release_date_formatted = datetime.strptime(release_date, '%Y-%m-%d').strftime('%d %B %Y')
        st.subheader(f"Date de sortie: {release_date_formatted}")
        st.write(f"#### Genres : {genres}")
        st.write("#### Résumé (en anglais)")
        st.write(overview)

    st.write(f"#### Note moyenne : {vote_average:.2f} / 10")
    st.write(f"#### Nombre de votes : {vote_count}")


def get_genre_distribution_by_year(year: int):
    """
    Récupère la distribution des genres de films pour une année donnée via l'API.

    Args:
        year (int): Année de sortie des films.

    Returns:
        dict | None: Un dictionnaire contenant la liste des genres et leur fréquence pour l'année donnée,
                     ou None si la requête échoue.
    """
    response = requests.get(f"{BACKEND_URL}/statistics/distribution_genres/{year}")
    return response.json() if response.status_code == 200 else None
