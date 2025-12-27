import requests
import json
import time
import logging
from dotenv import load_dotenv
import os

# Charger le .env pour récupérer TMDB_BEARER_TOKEN
load_dotenv()
logger = logging.getLogger(__name__)

TMDB_BEARER_TOKEN = os.getenv("TMDB_BEARER_TOKEN")
if not TMDB_BEARER_TOKEN:
    logger.error("❌ TMDB_BEARER_TOKEN non trouvé dans .env")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TMDB_BEARER_TOKEN}",
    "Accept": "application/json"
}

def load_movie_metadata(max_pages: int = 5):
    """
    Récupère les films populaires depuis TMDB en utilisant le Bearer Token v4
    et écrit le résultat dans data/movies_database.json
    """
    base_url = "https://api.themoviedb.org/3/movie/popular"
    all_movies = []
    for page in range(1, max_pages + 1):
        logger.info(f"🔄 Chargement de la page {page}...")
        resp = requests.get(base_url, headers=HEADERS, params={"language": "en-US", "page": page})
        if resp.status_code != 200:
            logger.error(f"❌ Erreur HTTP {resp.status_code} sur TMDB page {page}")
            break
        data = resp.json().get("results", [])
        if not data:
            logger.info("⚠️ Plus de résultats disponibles.")
            break
        all_movies.extend(data)
        time.sleep(0.2)
    # Sauvegarde JSON
    os.makedirs("data", exist_ok=True)
    with open("backend/app/utils/data/movies_database.json", "w", encoding="utf-8") as f:
        json.dump(all_movies, f, ensure_ascii=False, indent=4)
    logger.info(f"✅ {len(all_movies)} films enregistrés dans 'data/movies_database.json'.")

def load_genres():
    """
    Récupère la liste des genres depuis TMDB et l'écrit dans data/movies_genre.json
    """
    url = "https://api.themoviedb.org/3/genre/movie/list"
    logger.info("🔄 Chargement des genres TMDB...")
    resp = requests.get(url, headers=HEADERS, params={"language": "en-US"})
    if resp.status_code != 200:
        logger.error(f"❌ Erreur HTTP {resp.status_code} lors de la récupération des genres")
        return
    data = resp.json().get("genres", [])
    os.makedirs("data", exist_ok=True)
    with open("backend/app/utils/data/movies_genre.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"✅ {len(data)} genres enregistrés dans 'data/movies_genre.json'.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    load_movie_metadata(max_pages=500)
    load_genres()
