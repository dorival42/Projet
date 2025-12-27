import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd


# Appliquer un style Seaborn épuré pour s'intégrer avec Streamlit
sns.set(style="whitegrid", palette="muted")


def plot_rating_distribution(movies):
    """
    Affiche la distribution des notes moyennes des films sous forme d'histogramme.

    Args:
        movies (list[dict]): Liste de films, chaque film étant représenté sous forme de dictionnaire 
                             contenant au moins la clé 'vote_average'.

    Returns:
        None. Le graphique est affiché via Streamlit.
    """
    df = pd.DataFrame(movies)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["vote_average"], bins=20, kde=True, ax=ax, color="skyblue")
    ax.set_title("Distribution des notes", fontsize=16, fontweight='bold')
    ax.set_xlabel("Note Moyenne", fontsize=14)
    ax.set_ylabel("Fréquence", fontsize=14)
    ax.tick_params(axis='both', labelsize=12)
    ax.set_facecolor('#f9f9f9')
    st.pyplot(fig)



def plot_movies_per_year(movies):
    """
    Affiche un graphique en barres du nombre de films par année de sortie.

    Args:
        movies (list[dict]): Liste de films avec une clé 'release_date' au format YYYY-MM-DD.

    Returns:
        None. Le graphique est affiché via Streamlit.
    """
    df = pd.DataFrame(movies)
    df["release_date"] = pd.to_datetime(df["release_date"], errors='coerce')
    df["year"] = df["release_date"].dt.year
    count_by_year = df["year"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    count_by_year.plot(kind="bar", ax=ax, color="cornflowerblue", edgecolor="black")
    ax.set_title("Nombre de films par an de 1903 a 2025", fontsize=16, fontweight='bold')
    ax.set_xlabel("Année", fontsize=14)
    ax.set_ylabel("Nombre de films", fontsize=14)

    
    for p in ax.patches:
        ax.annotate(f'{p.get_height()}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    xytext=(0, 5),
                    textcoords='offset points',
                    ha='center', va='bottom', fontsize=12)

    ax.set_facecolor('#f9f9f9')
    ax.tick_params(axis='both', labelsize=8,labelrotation=45,)
    st.pyplot(fig)


def plot_top_movies(movies, top_n=10):
    """
    Affiche un graphique en barres horizontales des films les mieux notés.

    Args:
        movies (list[dict]): Liste de films avec au minimum les clés 'vote_average' et 'title'.
        top_n (int): Nombre de films à afficher dans le classement (par défaut : 10).

    Returns:
        None. Le graphique est affiché via Streamlit.
    """
    df = pd.DataFrame(movies)
    top_movies = df.sort_values("vote_average", ascending=False).head(top_n)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=top_movies, x="vote_average", y="title", ax=ax, color="lightseagreen", edgecolor="black")
    ax.set_title(f"Top {top_n} films par note", fontsize=16, fontweight='bold')
    ax.set_xlabel("Note Moyenne", fontsize=14)
    ax.set_ylabel("Titre du Film", fontsize=14)

    for p in ax.patches:
        ax.annotate(f'{p.get_width():.2f}',
                    (p.get_width(), p.get_y() + p.get_height() / 2.),
                    xytext=(5, 0),
                    textcoords='offset points',
                    ha='left', va='center', fontsize=12)

    ax.set_facecolor('#f9f9f9')
    ax.tick_params(axis='both', labelsize=12)
    st.pyplot(fig)



def plot_genre_distribution_chart(data: dict, year: int):
    """
    Affiche un histogramme de la distribution des genres pour une année donnée à l'aide de Streamlit et Seaborn.
    """
    if not data or not data.get("genres"):
        st.warning("Aucune donnée de genre disponible pour cette année.")
        return

    df = pd.DataFrame(data["genres"])
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x="count", y="genre", data=df, ax=ax, palette="muted")
    ax.set_title(f"Distribution des genres en {year}")
    ax.set_xlabel("Nombre de films")
    ax.set_ylabel("Genre")
    plt.tight_layout()
    st.pyplot(fig)


