from fastapi import APIRouter, HTTPException, Depends, Query
from collections import Counter
from ..service.recommendation_service import recommend_movies
from ..models.schemas import (
    Film, FilmListResponse, RecommendRequest, Recommendation,
    RecommendResponse, TopFilm, ListTopFilm, StatisticsResponse,
    GenreStatistics, DistributionGenresResponse, GenreDistribution,
    FilmCountResponse
)
import duckdb
import os
from pathlib import Path
import pandas as pd
from app.utils.count_gender import count_gender

router = APIRouter()


def get_db_connection():
    """
    Génère une connexion DuckDB au fichier films_reco.db.

    Returns:
        DuckDBPyConnection: Connexion à la base de données.
    """
    films_path = Path(__file__).resolve().parents[2] / "app" / "utils" / "data" / "films_reco.db"
    con = duckdb.connect(films_path)
    try:
        yield con
    finally:
        con.close()


@router.get("/films/count", response_model=FilmCountResponse)
def get_total_films(con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Compte le nombre total de films dans la base de données.

    Returns:
        FilmCountResponse: Nombre total de films enregistrés.
    """
    result = con.execute("SELECT COUNT(*) FROM films").fetchone()
    return FilmCountResponse(total_films=result[0])


@router.get("/films", response_model=FilmListResponse)
def get_films(page: int = Query(1, ge=1, le=500), con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Récupère une liste paginée de 20 films.

    Args:
        page (int): Numéro de la page (entre 1 et 500).

    Returns:
        FilmListResponse: Liste de films pour la page demandée.
    """
    films_per_page = 20
    offset = (page - 1) * films_per_page
    result = con.execute(f"SELECT * FROM films LIMIT {films_per_page} OFFSET {offset}").fetchall()

    if not result:
        raise HTTPException(status_code=404, detail="Aucun film trouvé pour cette page.")

    films = [
        Film(
            film_id=row[0],
            title=row[1],
            genres=row[2],
            description=row[3],
            release_date=row[4],
            vote_average=row[5],
            vote_count=row[6],
            poster_path=row[7]
        )
        for row in result
    ]
    return FilmListResponse(films=films)


@router.get("/films/search", response_model=FilmListResponse)
def search_films_by_title(query: str, con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Recherche de films dont le titre contient le texte donné.

    Args:
        query (str): Terme à rechercher dans les titres.

    Returns:
        FilmListResponse: Liste des films correspondant à la recherche.
    """
    search_query = f"%{query}%"
    result = con.execute("SELECT * FROM films WHERE title LIKE ? LIMIT 10", [search_query]).fetchall()

    films = [
        Film(
            film_id=row[0],
            title=row[1],
            genres=row[2],
            description=row[3],
            release_date=row[4],
            vote_average=row[5],
            vote_count=row[6],
            poster_path=row[7]
        )
        for row in result
    ]
    return FilmListResponse(films=films)


@router.get("/films/{id}", response_model=Film)
def get_film_by_id(id: int, con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Récupère les détails d’un film par son identifiant.

    Args:
        id (int): Identifiant du film.

    Returns:
        Film: Détail du film.
    """
    query = "SELECT * FROM films WHERE id = ?"
    row = con.execute(query, [id]).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Film introuvable.")
    return Film(
        film_id=row[0],
        title=row[1],
        genres=row[2],
        description=row[3],
        release_date=row[4],
        vote_average=row[5],
        vote_count=row[6],
        poster_path=row[7]
    )


@router.post("/recommendation_movies/{user_id}", response_model=RecommendResponse)
def get_recommendations(user_id: int, num_recommendations: int = 5):
    """
    Renvoie une liste de films recommandés pour un utilisateur.

    Args:
        user_id (int): Identifiant de l'utilisateur.
        num_recommendations (int): Nombre de recommandations souhaitées.

    Returns:
        RecommendResponse: Liste de films recommandés.
    """
    return recommend_movies(user_id, num_recommendations)


@router.get("/statistics/{year}", response_model=ListTopFilm)
def get_top10_film(year: int, con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Récupère les 10 meilleurs films (par vote moyen) pour une année donnée.

    Args:
        year (int): Année cible.

    Returns:
        ListTopFilm: Liste des 10 meilleurs films de l’année.
    """
    top_films_query = """
    SELECT title, vote_average, release_date
    FROM films
    WHERE STRFTIME('%Y', release_date) = ?
    ORDER BY vote_average DESC
    LIMIT 10
    """
    top_films = con.execute(top_films_query, [str(year)]).fetchall()
    if not top_films:
        raise HTTPException(status_code=404, detail="No films found for the given year.")

    return ListTopFilm(top_films=[
        TopFilm(title=row[0], vote_average=row[1], release_date=row[2]) for row in top_films
    ])


@router.get("/statistics/distribution_genres/{year}", response_model=DistributionGenresResponse)
def distribution_genres(year: int, con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Donne la distribution des genres pour une année donnée.

    Args:
        year (int): Année cible.

    Returns:
        DistributionGenresResponse: Liste des genres et leur fréquence.
    """
    genre_query = """
    SELECT genres
    FROM films
    WHERE STRFTIME('%Y', release_date) = ?
    """
    rows = con.execute(genre_query, [str(year)]).fetchall()
    genre_strings = [row[0] for row in rows if row[0]]
    if not genre_strings:
        raise HTTPException(status_code=404, detail="No genre data found for the given year.")

    genre_counter = count_gender(genre_strings)
    sorted_genres = sorted(genre_counter.items(), key=lambda x: x[1], reverse=True)

    return DistributionGenresResponse(
        year=year,
        genres=[GenreDistribution(genre=genre, count=count) for genre, count in sorted_genres]
    )


@router.get("/statistics/{gender}/{year}", response_model=StatisticsResponse)
def get_statistics(gender: str, year: int, con: duckdb.DuckDBPyConnection = Depends(get_db_connection)):
    """
    Récupère les 10 meilleurs films pour un genre et une année donnés,
    ainsi que le nombre total de films de ce genre cette année-là.

    Args:
        gender (str): Genre recherché (ex. "Action").
        year (int): Année cible.

    Returns:
        StatisticsResponse: Top 10 des films + statistiques de genre.
    """
    top_films_query = """
    SELECT title, vote_average, release_date
    FROM films
    WHERE STRFTIME('%Y', release_date) = ? AND genres LIKE ?
    ORDER BY vote_average DESC
    LIMIT 10
    """
    top_films = con.execute(top_films_query, [str(year), f'%{gender}%']).fetchall()
    if not top_films:
        raise HTTPException(status_code=404, detail="No films found for the given year.")

    genre_stats_query = """
    SELECT genres
    FROM films
    WHERE STRFTIME('%Y', release_date) = ? AND genres LIKE ?
    """
    genre_stats = con.execute(genre_stats_query, [str(year), f'%{gender}%']).fetchall()
    genre_strings = [row[0] for row in genre_stats if row[0]]
    genre_counter = count_gender(genre_strings)

    return StatisticsResponse(
        top_films=[
            TopFilm(title=row[0], vote_average=row[1], release_date=row[2]) for row in top_films
        ],
        genre_statistics=GenreStatistics(genre=gender, count=genre_counter[gender])
    )
