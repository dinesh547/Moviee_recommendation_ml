import streamlit as st
import joblib
import requests

# Page configuration
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# Optional: Add your free TMDB API key to display movie posters
# Get one at: https://themoviedb.org
TMDB_API_KEY = "71a525bee8baa9f0fbfc8090bc29d2fd"
PLACEHOLDER_POSTER = "https://placeholder.com"


@st.cache_resource
def load_data():
    movies = joblib.load("movies.pkl")
    similarity = joblib.load("similarity.pkl")
    return movies, similarity


def fetch_poster(movie_id):
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        return PLACEHOLDER_POSTER

    url = f"https://themoviedb.org{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://tmdb.org{poster_path}"
    except requests.RequestException:
        pass
    return PLACEHOLDER_POSTER


def recommend(movie_title, movies, similarity):
    movie_index = movies[movies["title"] == movie_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []
    for i in movies_list:
        row = movies.iloc[i[0]]
        recommended_titles.append(row.title)
        recommended_posters.append(fetch_poster(row.id))

    return recommended_titles, recommended_posters


# Load model artifacts once and cache them
movies, similarity = load_data()

# UI Layout
st.title("🎬 Movie Recommender System")
st.write("Select a movie you like to get 5 similar recommendations.")

selected_movie = st.selectbox(
    "Search or select a movie:",
    movies["title"].values
)

if st.button("Recommend", type="primary"):
    with st.spinner("Finding similar movies..."):
        titles, posters = recommend(selected_movie, movies, similarity)

    st.subheader(f"Because you watched **{selected_movie}**:")
    cols = st.columns(5)
    for col, title, poster in zip(cols, titles, posters):
        with col:
            st.image(poster, use_container_width=True)
            st.caption(f"**{title}**")
