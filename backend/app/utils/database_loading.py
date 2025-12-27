from sqlalchemy import insert, ForeignKey,Sequence, create_engine,Integer,Date,String,Float,Column,func,PrimaryKeyConstraint
from sqlalchemy.orm import declarative_base,sessionmaker,relationship
from sqlalchemy.exc import IntegrityError
import pandas as pd
import json
import logging
import time
from datetime import datetime

# Définition de la base
# Connexion à DuckDB
engine = create_engine('duckdb:///data/films_reco.db')
Base = declarative_base()
SessionLocal= sessionmaker(bind=engine)
session= SessionLocal()



class Film(Base):
    __tablename__ = 'films'
    id = Column(Integer,Sequence('film_id_seq'), primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(String, nullable=True)  # Les genres peuvent être nulls si pas définis
    description = Column(String, nullable=True)
    release_date = Column(Date, nullable=True)  # Utilisation du type Date pour la date
    vote_average = Column(Float, nullable=True)  # Note en nombre à virgule flottante
    vote_count = Column(Integer, nullable=True)  # Compte des votes en entier
    #ratings = relationship("Rating", back_populates="film", cascade="all, delete-orphan")

    
    def __repr__(self):
        return f"<Rating(film_id={self.id},name={self.title},date={self.release_date},rating={self.vote_average})>"

# Définition de la classe Ratings
class Rating(Base):
    __tablename__ = 'ratings'
    user_id = Column(Integer,nullable=False)
    film_id = Column(Integer,nullable=False)
    rating = Column(Float,nullable=False)
    timestamp= Column(Integer,nullable=False)

    #film = relationship("Film", back_populates="ratings")
    
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'film_id'),
    )

    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, movie_id={self.film_id}, rating={self.rating})>"


# Création des tables
Base.metadata.create_all(engine)


def add_film_from_json():
    session = SessionLocal()
    # Charger les films depuis un JSON
    with open("data/movies_database.json", "r", encoding="utf-8") as f:
        all_movies = json.load(f)

    # Charger les genres
    with open("data/movies_genre.json", "r", encoding="utf-8") as f:
        genre_data = json.load(f)

    # Créer un dictionnaire {id: nom}
    genre_map = {g["id"]: g["name"] for g in genre_data}

    # Liste des films à insérer
    films_to_insert = []

    for movie in all_movies:
        
        genre_names = [genre_map.get(gid, str(gid)) for gid in movie.get("genre_ids", [])]
        genre_string = ",".join(genre_names) if genre_names else None

        # Convertir la release_date en Date si elle est valide
        release_date_str = movie.get("release_date")
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, "%Y-%m-%d").date()  # Convertir en objet Date
            except ValueError:
                print(f"Date invalide pour le film {movie.get('title')}, ID: {movie.get('id')}")
                release_date = None
        else:
            release_date = None

        # Vérifier si le film est déjà dans la liste films_to_insert (en vérifiant l'ID)
        if any(film.id == movie.get("id") for film in films_to_insert):
            print(f"Le film {movie.get('title')} avec l'ID {movie.get('id')} est déjà dans la liste des films à insérer.")
            continue  # Si le film est déjà dans films_to_insert, on passe au film suivant

        # Ajouter le film à la liste pour insertion
        films_to_insert.append(Film(
            id=movie.get("id"),
            title=movie.get("title"),
            genres=genre_string,
            description=movie.get("overview"),
            release_date=release_date,
            vote_average=movie.get("vote_average"),
            vote_count=movie.get("vote_count")
        ))

    # Insérer dans la base si la liste n'est pas vide
    for film in films_to_insert:
        session.add(film)
    
    session.commit()  # Commiter après avoir ajouté tous les films
    session.close()

    # Vérification (afficher quelques films pour vérifier que l'insertion a fonctionné)
    print("\nFilms insérés ou mis à jour :")
    for film in session.query(Film).limit(5):
        print(film)

# Configurer les logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_rating_from_csv():
    # Définir la taille des lots
    BATCH_SIZE = 25000
    try:
        # Lire les données depuis le CSV avec pandas
        logger.info("Lecture des données depuis le fichier CSV...")
        df = pd.read_csv('data/ratings.csv')

        # Vérifier le nombre de lignes lues
        logger.info(f"Nombre de lignes lues depuis le fichier CSV : {len(df)}")

        # Initialiser un compteur pour suivre les lignes insérées
        total_inserted = 0

        # Insérer les données par lots
        for start in range(0, len(df), BATCH_SIZE):
            # Prendre un sous-ensemble des données pour ce lot
            batch = df.iloc[start:start+BATCH_SIZE]
            
            # Convertir les données du DataFrame en un format adapté à l'insertion
            insert_data = [
                {"user_id": row["userId"], "film_id": row["movieId"], "rating": row["rating"], "timestamp": row["timestamp"]}
                for _, row in batch.iterrows()
            ]

            # Créer une instruction d'insertion avec "Insert Many Values"
            stmt = insert(Rating).values(insert_data)

            # Mesurer le temps d'insertion
            start_time = time.time()

            # Exécuter l'insertion en utilisant la méthode "execute"
            session.execute(stmt)

            # Commit les changements pour ce lot
            session.commit()

            # Calculer le temps écoulé pour ce lot
            elapsed_time = time.time() - start_time

            # Mettre à jour le compteur du total des lignes insérées
            total_inserted += len(batch)

            # Log la vitesse d'insertion pour ce lot
            logger.info(f"{len(batch)} lignes insérées en {elapsed_time:.2f} secondes.")
            
            # Optionnel : Afficher le nombre total de lignes insérées jusqu'à présent
            logger.info(f"Total des lignes insérées jusqu'à présent : {total_inserted}")

    except Exception as e:
        logger.error(f"Une erreur est survenue : {e}")
        session.rollback()  # Rollback en cas d'erreur

    finally:
        # Vérification : récupérer et afficher les premières lignes insérées
        logger.info("Vérification des données insérées...")
        ratings = session.query(Rating).limit(10).all()
        for rating in ratings:
            logger.info(f'UserID: {rating.user_id}, MovieID: {rating.film_id}, Rating: {rating.rating}, Timestamp: {rating.timestamp}')

        # Fermer la session
        session.close()
        logger.info("Session fermée.")

if __name__ =="__main__":

    add_film_from_json()
    add_rating_from_csv()
    
    session.close()

