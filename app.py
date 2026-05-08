import os
from pathlib import Path
import streamlit as st
import pickle
import requests
import random
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from scipy.sparse import load_npz

def get_api_secret(key: str) -> str:
    """Return secret from Streamlit secrets or environment variables."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

API_KEY = get_api_secret("TMDB_API_KEY")
OMDB_API_KEY = get_api_secret("OMDB_API_KEY")

# Initialize session state
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

@st.cache_resource
def get_session():
    """Create a requests session with retry logic"""
    session = requests.Session()
    retry = Retry(
        connect=2, 
        backoff_factor=0.3, 
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@st.cache_resource
def init_poster_cache():
    """Initialize poster cache as empty dict"""
    return {}

poster_cache = init_poster_cache()

@st.cache_data
def fetch_poster(movie_id, title=None):
    """Fetch poster from TMDB first, then OMDb, then local placeholder."""
    cache_key = f"{movie_id}-{title or ''}"
    if cache_key in poster_cache:
        return poster_cache[cache_key]

    def local_placeholder():
        poster_colors = [
            "https://via.placeholder.com/500x750/FF6B6B/FFFFFF?text=Movie+Poster",
            "https://via.placeholder.com/500x750/4D2FB2/FFFFFF?text=Movie+Poster",
            "https://via.placeholder.com/500x750/FFD93D/000000?text=Movie+Poster",
            "https://via.placeholder.com/500x750/FF8C42/FFFFFF?text=Movie+Poster",
            "https://via.placeholder.com/500x750/6BCB77/FFFFFF?text=Movie+Poster",
        ]
        poster_url = poster_colors[movie_id % len(poster_colors)]
        poster_cache[cache_key] = poster_url
        return poster_url

    try:
        session = get_session()
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = session.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()
        if data.get("poster_path"):
            poster_url = "https://image.tmdb.org/t/p/original" + data["poster_path"]
            poster_cache[cache_key] = poster_url
            return poster_url
    except Exception:
        pass

    if OMDB_API_KEY and title:
        try:
            omdb_url = "http://www.omdbapi.com/"
            params = {"t": title, "apikey": OMDB_API_KEY}
            response = session.get(omdb_url, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()
            if data.get("Poster") and data.get("Poster") != "N/A":
                poster_cache[cache_key] = data["Poster"]
                return data["Poster"]
        except Exception:
            pass

    return local_placeholder()


# st.set_page_config(
#     page_title="Movie Recommender",
#     page_icon="🎬",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     # initial_sidebar_state="collapsed"
# )

# Custom CSS with Background Image and Styling
# Custom CSS
page_element="""
<style>
[data-testid="stAppViewContainer"]{
  background-image: url("https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
  background-size: cover;
}
[data-testid="stHeader"]{
  background-color: rgba(0,0,0,0);
}
.stButton > button {
    background-color: #4D2FB2;         
    color: white;
}
</style>
"""

st.markdown(page_element, unsafe_allow_html=True)
st.markdown("""
<style>
    /* Background image */
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://images.unsplash.com/photo-1595769816263-9b910be24d5f?q=80&w=1179&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Header styling */
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    
    /* Main container overlay */
    .main {
        background: rgba(20, 20, 40, 0.85) !important;
    }
    
    /* Title styling */
    h1 {
        color: #FF6B6B;
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    
    /* Subtitle */
    h2, h3 {
        color: #FFD93D;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.1);
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8C42);
        color: white;
        font-weight: bold;
        font-size: 16px;
        padding: 10px 30px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
    }
    
    /* Text styling */
    p, label {
        color: #E8E8E8;
    }
    
    /* Container styling */
    [data-testid="column"] {
        background: rgba(40, 40, 60, 0.6);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    /* Image styling */
    img {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease;
    }
    
    img:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# st.title("🎬 Movie Recommender System")
# st.markdown("---")
# st.markdown("### Find Your Next Favorite Movie 🍿")
# st.markdown("")

@st.cache_resource
def load_data():
    """Load pickle files once and cache them"""
    for filepath in ["movies_df.pkl", "similarity_mat.npz"]:
        if not Path(filepath).exists():
            raise FileNotFoundError(
                f"Required deployment file is missing: {filepath}. "
                "Make sure it is tracked in GitHub and present in the repo root."
            )

    try:
        movies_df = pickle.load(open("movies_df.pkl", "rb"))
        similarity_sparse = load_npz("similarity_mat.npz")
    except Exception as e:
        raise RuntimeError(f"Failed to load deployment data files: {e}") from e

    return movies_df, similarity_sparse

movies_df, similarity_df = load_data()

def recommend(movie): # very similar to what we'have build
    '''return 5 similar movies'''
    movie_index = movies_df[movies_df["title"].str.lower() == movie.lower()].index[0] # .[0] think like .index is
    # a box and we take first element -> [0][0] -> 0
    distances = similarity_df[movie_index].toarray().flatten()  # Convert sparse to dense array
    movies_list = sorted(
        list(enumerate(distances)),  # (index, similarity_score)
        reverse=True, # descending order
        key=lambda x: x[1]) # sorting on similarity wale pr not on index pr
    top_5 = movies_list[1:6]  

    recommended_movies = []
    recommend_movies_posters = []
    for i in top_5:
        # recommended_movies.append(movies_df.iloc[i[0]].title) 
        # # fetch posters from API
        # recommend_movies_posters.append(fetch_poster(movies_df.iloc[i[0]].movie_id))
        # print(movies_df.iloc[i[0]].movie_id)
        # fetch the movie poster
        movie_id = movies_df.iloc[i[0]].movie_id
        movie_title = movies_df.iloc[i[0]].title
        recommend_movies_posters.append(fetch_poster(movie_id, movie_title))
        recommended_movies.append(movie_title)

    return recommended_movies, recommend_movies_posters 

movies_titles = movies_df["title"].values

# Custom CSS
st.markdown("""
<style>
    /* Modern card design */
    .movie-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        border-color: rgba(255,107,107,0.5);
    }

    /* Search box styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.1);
        color: white;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.3);
        padding: 10px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF6B6B;
        box-shadow: 0 0 10px rgba(255,107,107,0.3);
    }

    /* Button improvements */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8C42);
        color: white;
        font-weight: bold;
        font-size: 16px;
        padding: 12px 25px;
        border-radius: 25px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
        transition: all 0.3s ease;
        margin: 5px;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
    }

    /* Random button special styling */
    .random-btn > button {
        background: linear-gradient(135deg, #4D2FB2, #6BCB77);
    }
    .random-btn > button:hover {
        background: linear-gradient(135deg, #6BCB77, #4D2FB2);
    }

    /* Movie title styling */
    .movie-title {
        color: #FFD93D;
        font-weight: bold;
        font-size: 16px;
        margin: 12px 0 4px 0;
        text-align: left;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }

    /* Card layout */
    .movie-card {
        width: 100%;
        min-height: 410px;
        border-radius: 16px;
        overflow: hidden;
        position: relative;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.18);
    }

    .movie-card:hover {
        transform: translateY(-5px);
    }

    .poster-image {
        width: 100%;
        height: 430px;
        object-fit: cover;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    }

    .movie-name {
        color: #ffffff;
        font-weight: 700;
        font-size: 16px;
        margin-top: 10px;
        text-align: left;
        line-height: 1.2;
    }

    /* Full width page container */
    .css-1d391kg {
        max-width: 100%;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    .block-container {
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    .main {
        align-items: flex-start;
    }

    .stButton > button {
        width: 100% !important;
        display: block;
    }

    .stTextInput > div > div > input {
        min-width: 100%;
    }

    .stSelectbox > div > div > div {
        min-width: 100%;
    }

    /* Image styling */
    img {
        border-radius: 16px;
        transition: transform 0.3s ease;
    }
    img:hover {
        transform: scale(1.03);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("---")
st.markdown("## 🎬 Movie Recommender System")
st.markdown("### 🍿 Discover Your Next Favorite Movie")

# Search and Random Section
col1, col2 = st.columns([3, 1])

with col1:
    # Search box for movie selection
    search_query = st.text_input(
        "🔍 Search for a movie:",
        placeholder="Type movie name...",
        help="Start typing to find movies"
    )

    # Filter movies based on search
    filtered_movies = [movie for movie in movies_titles if search_query.lower() in movie.lower()] if search_query else list(movies_titles)
    if search_query and not filtered_movies:
        st.warning("No movies found. Try a different search term.")

    user_selected_movie = st.selectbox(
        "🎥 Select a movie:",
        filtered_movies,
        help="Choose a movie to get recommendations"
    )

with col2:
    # Random recommendation button
    if st.button("🎲 Random Movie", use_container_width=True, key="random"):
        user_selected_movie = random.choice(movies_titles)
        st.session_state.selected_movie = user_selected_movie
        st.rerun()

# Show selected movie
if user_selected_movie:
    st.success(f"Selected: **{user_selected_movie}**")

# Recommendation buttons
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    recommend_btn = st.button("🎯 Get Recommendations", use_container_width=True)

with col2:
    if st.button("🔄 Clear", use_container_width=True):
        st.session_state.selected_movie = None
        st.session_state.recommendations = None
        st.rerun()

# Recommendations Display
if recommend_btn and user_selected_movie:
    with st.spinner("Finding your perfect matches... 🎬"):
        names, posters = recommend(user_selected_movie)
        st.session_state.recommendations = (names, posters)

if st.session_state.recommendations:
    names, posters = st.session_state.recommendations

    st.markdown("---")
    st.markdown(f"## 🌟 Top 5 Recommendations for **{user_selected_movie}**")
    st.markdown("")

    # Display recommendations in a grid
    cols = st.columns(5, gap="small")

    for i in range(len(names)):
        with cols[i]:
            movie_name = names[i]
            st.markdown(f"""
                <div class="movie-card">
                    <img class="poster-image" src="{posters[i]}" alt="{movie_name}" />
                </div>
                <div class="movie-name">{i+1}. {movie_name}</div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Search for movies or click 'Random Movie' to explore!")
st.markdown("🔒 Your data stays private and secure.")
    