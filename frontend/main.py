import streamlit as st
import pandas as pd
from app.utils.api import get_all_movies, get_user_recommendations, afficher_film_complet, get_genre_distribution_by_year
from app.utils.charts import (
    plot_rating_distribution,
    plot_movies_per_year,
    plot_top_movies,
    plot_genre_distribution_chart
)
from app.utils.logs import visual_log, display_logs
from datetime import datetime

st.set_page_config(
    page_title="HomeFlix",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🎬 HomeFlix")
section = st.sidebar.radio("Navigation", [
    "🏠 Accueil",
    "📊 Statistiques des films",
    "📅 Statistiques par genre et année",
    "🎯 Recommandations personnalisées",
    "🎬 Détails d'un Film"
])

st.title("🎥 Tableau de bord de recommandations de films")
if section == "🏠 Accueil":
    st.markdown("""
    ### 🎥 Bienvenue sur HomeFlix !

    HomeFlix est une **plateforme de recommandation de films** qui vise à offrir à chaque utilisateur ou utilisatrice une expérience de visionnage **personnalisée**, en fonction de ses goûts et préférences.

    ---
    
    ## 🧭 Navigation
    - **📊 Statistiques des films** : Visualisez les tendances générales des films (notes, années de sortie, etc.).
    - **📅 Statistiques par genre et année** : Découvrez les meilleurs films pour un genre et une année donnée.
    - **🎯 Recommandations personnalisées** : Obtenez des suggestions personnalisées selon un ID utilisateur.
    - **🎬 Détails d'un Film : Permet d'afficher les détails d'un film par son ID

    ---
    
    ## 📁 Sources de données
    Les données utilisées dans ce projet proviennent de [TMDB](https://www.themoviedb.org/), enrichies pour permettre la recommandation de films.

    ---
    
    👨‍💻 Projet réalisé dans le cadre d’un projet pédagogique / personnel.

    """, unsafe_allow_html=True)
elif section == "📊 Statistiques des films":
    # # Choix de la page pour charger les films
    # page_num = st.sidebar.number_input(
    #     "Page des films à charger", min_value=1, max_value=100, value=1
    # )
    # st.subheader(f"Chargement des films - Page {page_num}")
    
    # # Liste pour stocker tous les films
    # all_movies = []
    
    # # Variable pour savoir si la dernière page valide a été trouvée
    # last_valid_page = page_num
    
    # # On essaie de récupérer les films de chaque page depuis 1 jusqu'à la page spécifiée
    # for page in range(1, page_num + 1):
    #     movies = get_all_movies(page=page)
        
    #     if not movies:
    #         st.warning(f"Impossible de récupérer les films pour la page {page}. Tentative avec la page précédente.")
            
    #         # Si la page échoue, on garde la dernière page valide trouvée
    #         last_valid_page = page - 1
    #         break  # Arrêter la recherche dès qu'on a une erreur
        
    #     visual_log(f"{len(movies)} films chargés depuis la page {page}", "SUCCESS")
    #     all_movies.extend(movies)  # Ajout des films récupérés à la liste all_movies
    
    # # Si une erreur est survenue, on essaye de récupérer la page valide la plus proche
    # if not all_movies and last_valid_page > 0:
    #     st.warning(f"En raison d'erreurs sur les pages, on affiche les statistiques des films de la page {last_valid_page}.")
    #     # Récupère les films de la dernière page valide
    #     all_movies = get_all_movies(page=last_valid_page)
    #     visual_log(f"Films chargés depuis la page {last_valid_page} (page de secours)", "SUCCESS")
    # Récupérer tous les films disponibles
    all_movies = get_all_movies()  # Cette fonction récupère tous les films en combinant les pages
    
    # Affichage des statistiques avec tous les films combinés
    if all_movies:
        st.subheader("Distribution des notes")
        plot_rating_distribution(all_movies)

        st.subheader("Nombre de films par année")
        plot_movies_per_year(all_movies)

        st.subheader("Top 10 des films les mieux notés")
        plot_top_movies(all_movies, top_n=10)
    else:
        st.error("Aucun film n'a été récupéré pour afficher les statistiques.")
        visual_log("Échec du chargement des films", "ERROR")

elif section == "🎯 Recommandations personnalisées":
    st.subheader("🔍 Rechercher des recommandations")

    with st.form("user_form"):
        user_id = st.number_input("Entrer l'ID utilisateur", min_value=1, step=1)
        num_reco = st.slider("Nombre de recommandations", 1, 20, 5)
        submitted = st.form_submit_button("Obtenir les recommandations")

    if submitted:
        try:
            reco_user = get_user_recommendations(user_id, num_reco)
            recommendations = reco_user["recommendations"]
            
            if recommendations:
                st.success(f"Voici {len(recommendations)} recommandations pour l'utilisateur {user_id}:")
                
                # Créer des colonnes pour l'affichage des films
                cols = st.columns(4)  # 5 films par ligne
                for i, film in enumerate(recommendations):
                    with cols[i % 4]:
                        # Affiche l'affiche si disponible
                        with st.container(height=400,border=False):
                            poster = film.get('poster_path')
                            if poster:
                                image_url = f"https://image.tmdb.org/t/p/w300{poster}"
                                st.image(image_url, width=200)
                            st.write("Titre: ",film['title'])
                            st.write("Id_film ",film['movie_id'])
                                    
                    # Ajouter un petit écart entre chaque ligne de films
                    if (i + 1) % 5 == 0:
                        st.write("") 


            else:
                st.warning("Aucune recommandation trouvée pour cet utilisateur.")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des recommandations : {e}")

elif section == "🎬 Détails d'un Film":
    st.subheader("Afficher un film en détails")
    film_id = st.number_input("ID du Film", min_value=1, step=1)
    
    if st.button("Afficher le Film"):
        afficher_film_complet(film_id)


elif section == "📅 Statistiques par genre et année":


    st.subheader("🎞️ Filtrer par genre et année")
    GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary",
    "Drama", "Family", "Fantasy", "History", "Horror", "Music",
    "Mystery", "Romance", "Science Fiction", "TV Movie", "Thriller",
    "War", "Western"
]

    genre = st.selectbox("Genre", options=GENRES, index=GENRES.index("Action"))

    # genre = st.text_input("Genre (en anglais)", value="Action")
    year_stat_genre = st.number_input("Année", min_value=1930, max_value=2026, value=2020)

    if st.button("Afficher les statistiques"):
        from app.utils.api import get_statistics_by_genre_year
        try:
            data = get_statistics_by_genre_year(genre, year_stat_genre)

            if not data:
                st.warning("Aucune donnée trouvée pour cette combinaison genre/année.")
            else:
                # Afficher les meilleurs films
                top_films = data["top_films"]
                if top_films:
                    st.markdown(f"### 🎬 Top {len(top_films)} films {genre.title()} en {year_stat_genre}")
                    df = pd.DataFrame(top_films)
                    df = df.rename(columns={
                        "title": "Titre",
                        "release_date": "Date de sortie",
                        "vote_average": "Note moyenne"
                        })
                    df["Note moyenne"] = df["Note moyenne"].round(2)
                    st.dataframe(df)
                else:
                    st.info("Aucun film trouvé pour ce genre et cette année.")

                # Afficher les statistiques du genre
                genre_stats = data["genre_statistics"]
                st.markdown("### 📊 Statistiques du genre")
                st.write(f"Le genre **{genre.title()}** apparaît dans **{genre_stats['count']}** films en {year_stat_genre}.")

        except Exception as e:
            st.error(f"Erreur lors de la récupération des statistiques : {e}")

    st.subheader("🎬 Distribution des genres par année")
    year = st.number_input("Choisissez une année", min_value=1900, max_value=2030, value=2020)
    if st.button("Afficher la distribution des genres"):
        distribution_genres = get_genre_distribution_by_year(year)
        plot_genre_distribution_chart(distribution_genres, year)

