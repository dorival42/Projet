from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, field_validator

# Pydantic models
class Film(BaseModel):
    film_id: int
    title: str
    genres: str
    description: str
    release_date: date
    vote_average: float
    vote_count: int
    poster_path: Optional[str] = None

class FilmListResponse(BaseModel):
    films: List[Film]


# Définition de la classe pour la requête
class RecommendRequest(BaseModel):
    num_recommendations: Optional[int] = 5  # Nombre de recommandations à retourner

# Définition de la classe pour une recommandation individuelle
class Recommendation(BaseModel):
    movie_id: int
    title: str
    rating_predicted: float
    poster_path: Optional[str] = None

    @field_validator("rating_predicted")
    @classmethod
    def round_rating(cls, v):
        return round(v, 1)

# Définition de la classe pour la réponse
class RecommendResponse(BaseModel):
    user_id: int
    recommendations: List[Recommendation]

    

class TopFilm(BaseModel):
    title: str
    vote_average: float
    release_date: date
class ListTopFilm(BaseModel):
    top_films:List[TopFilm]
class GenreStatistics(BaseModel):
    genre: str
    count: int

class StatisticsResponse(BaseModel):
    top_films: List[TopFilm]
    genre_statistics: GenreStatistics

class GenreDistribution(BaseModel):
    genre: str
    count: int

class DistributionGenresResponse(BaseModel):
    year: int
    genres: List[GenreDistribution]

class FilmCountResponse(BaseModel):
    total_films: int

