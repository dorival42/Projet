import streamlit as st
from app.utils.api import get_all_movies, get_user_recommendations
from app.utils.charts import (
    plot_rating_distribution,
    plot_movies_per_year,
    plot_top_movies
)

st.set_page_config(
    page_title="Film Recommender Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🎬 Film Recommender")
section = st.sidebar.radio("Navigation", [
    "📊 Statistiques des films",
    "🎯 Recommandations personnalisées",
    "🌟 Films populaires"
])

st.title("🎥 Tableau de bord de recommandations de films")

if section == "📊 Statistiques des films":
    # Choix de la page pour charger les films
    page_num = st.sidebar.number_input(
        "Page des films à charger", min_value=1, max_value=100, value=1
    )
    st.subheader(f"Chargement des films - Page {page_num}")
    movies = get_all_movies(page=page_num)

    if not movies:
        st.error("Impossible de récupérer les films pour cette page.")
    else:
        st.subheader("Distribution des notes")
        plot_rating_distribution(movies)

        st.subheader("Nombre de films par année")
        plot_movies_per_year(movies)

        st.subheader("Top 10 des films les mieux notés")
        plot_top_movies(movies, top_n=10)

elif section == "🎯 Recommandations personnalisées":
    st.subheader("🔍 Rechercher des recommandations")

    with st.form("user_form"):
        user_id = st.number_input("Entrer l'ID utilisateur", min_value=1, step=1)
        num_reco = st.slider("Nombre de recommandations", 1, 20, 5)
        submitted = st.form_submit_button("Obtenir les recommandations")

    if submitted:
        try:
            recommendations = get_user_recommendations(user_id, num_reco)
            if recommendations:
                st.success(f"Voici {len(recommendations)} recommandations pour l'utilisateur {user_id}:")
                cols = st.columns(5)
                for i, film in enumerate(recommendations):
                    with cols[i % 5]:
                        # Affiche l'affiche si disponible
                        poster = film.get('poster_path')
                        if poster:
                            st.image(poster, width=120)
                        st.caption(film.get('title', 'Titre inconnu'))
            else:
                st.warning("Aucune recommandation trouvée pour cet utilisateur.")
        except Exception as e:
            st.error(f"Erreur lors de la récupération des recommandations : {e}")


# Section pour les films populaires
elif section == "🌟 Films populaires":
    # Choix de la page pour charger les films
    page_num = st.sidebar.number_input(
        "Page des films à charger", min_value=1, max_value=100, value=1
    )
    st.subheader(f"🎬 Liste des films populaires - Page {page_num}")

    # Charger les films populaires
    popular_movies = get_all_movies(page=page_num)  # On suppose que la page 1 contient les films populaires
    if not popular_movies:
        st.error("Impossible de récupérer les films populaires.")
    else:
        # Affichage des films populaires avec titre, popularité et date de sortie
        for film in popular_movies[:5]:  # Limiter à 5 films populaires pour ne pas surcharger l'interface
            st.write(f"**{film.get('title', 'Titre inconnu')}**")
            st.write(f"🎬 Moyenne vote: {film.get('vote_average', 'N/A')}")
            st.write(f"📅 Date de sortie: {film.get('release_date', 'N/A')}")
            st.markdown("---")