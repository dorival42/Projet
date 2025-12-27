from sqlalchemy import insert, ForeignKey, Sequence, create_engine, Integer, Date, String, Float, Column, func, PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import pandas as pd
import json
import logging
import time
from datetime import datetime

# Configuration de la base de données avec DuckDB
engine = create_engine('duckdb:///backend/app/utils/data/films_reco.db')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


class Film(Base):
    """
    Modèle SQLAlchemy représentant un film.
    """
    __tablename__ = 'films'
    id = Column(Integer, Sequence('film_id_seq'), primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(String, nullable=False)
    description = Column(String, nullable=False)
    release_date = Column(Date, nullable=True)
    vote_average = Column(Float, nullable=True)
    vote_count = Column(Integer, nullable=True)
    poster_path = Column(String, nullable=True)
    # ratings = relationship("Rating", back_populates="film", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rating(film_id={self.id},name={self.title},date={self.release_date},rating={self.vote_average})>"


class Rating(Base):
    """
    Modèle SQLAlchemy représentant une note donnée à un film par un utilisateur.
    Clé primaire composite sur (user_id, film_id).
    """
    __tablename__ = 'ratings'
    user_id = Column(Integer, nullable=False)
    film_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(Integer, nullable=False)

    # film = relationship("Film", back_populates="ratings")

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'film_id'),
    )

    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, movie_id={self.film_id}, rating={self.rating})>"


# Création des tables dans la base de données si elles n'existent pas déjà
Base.metadata.create_all(engine)


def add_film_from_json():
    """
    Charge les films depuis deux fichiers JSON (films + genres), puis insère les données
    dans la table 'films' en évitant les doublons.
    """
    session = SessionLocal()

    with open("backend/app/utils/data/movies_database.json", "r", encoding="utf-8") as f:
        all_movies = json.load(f)

    with open("backend/app/utils/data/movies_genre.json", "r", encoding="utf-8") as f:
        genre_data = json.load(f)

    genre_map = {g["id"]: g["name"] for g in genre_data}
    films_to_insert = []

    for movie in all_movies:
        genre_names = [genre_map.get(gid, str(gid)) for gid in movie.get("genre_ids", [])]
        genre_string = ",".join(genre_names) if genre_names else "" 

        release_date_str = movie.get("release_date")
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()
            except ValueError:
                print(f"Date invalide pour le film {movie.get('title')}, ID: {movie.get('id')}")
                release_date = None
        else:
            release_date = None

        if any(film.id == movie.get("id") for film in films_to_insert):
            print(f"Le film {movie.get('title')} avec l'ID {movie.get('id')} est déjà dans la liste des films à insérer.")
            continue

        films_to_insert.append(Film(
            id=movie.get("id"),
            title=movie.get("title"),
            genres=genre_string,
            description=movie.get("overview"),
            release_date=release_date,
            vote_average=movie.get("vote_average"),
            vote_count=movie.get("vote_count"),
            poster_path=movie.get("poster_path")
        ))

    for film in films_to_insert:
        session.add(film)

    session.commit()
    session.close()

    # Affiche un aperçu des films insérés
    print("\nFilms insérés ou mis à jour :")
    for film in session.query(Film).limit(5):
        print(film)


# Configuration du logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def add_rating_from_csv():
    """
    Charge les évaluations de films depuis un fichier CSV et les insère dans la table 'ratings'
    par lots pour améliorer les performances.
    """
    BATCH_SIZE = 25000
    try:
        logger.info("Lecture des données depuis le fichier CSV...")
        df = pd.read_csv('backend/app/utils/data/ratings.csv')
        logger.info(f"Nombre de lignes lues depuis le fichier CSV : {len(df)}")

        total_inserted = 0

        for start in range(0, len(df), BATCH_SIZE):
            batch = df.iloc[start:start + BATCH_SIZE]

            insert_data = [
                {
                    "user_id": row["userId"],
                    "film_id": row["movieId"],
                    "rating": row["rating"],
                    "timestamp": row["timestamp"]
                }
                for _, row in batch.iterrows()
            ]

            stmt = insert(Rating).values(insert_data)
            start_time = time.time()
            session.execute(stmt)
            session.commit()
            elapsed_time = time.time() - start_time

            total_inserted += len(batch)
            logger.info(f"{len(batch)} lignes insérées en {elapsed_time:.2f} secondes.")
            logger.info(f"Total des lignes insérées jusqu'à présent : {total_inserted}")

    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")
        session.rollback()

    finally:
        logger.info("Vérification des données insérées...")
        ratings = session.query(Rating).limit(10).all()
        for rating in ratings:
            logger.info(f'UserID: {rating.user_id}, MovieID: {rating.film_id}, Rating: {rating.rating}, Timestamp: {rating.timestamp}')
        session.close()
        logger.info("Session fermée.")


if __name__ == "__main__":
    add_film_from_json()
    # add_rating_from_csv()
    session.close()

