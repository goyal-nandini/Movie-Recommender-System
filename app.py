import os
import streamlit as st
import pickle
import requests
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from scipy.sparse import load_npz

API_KEY = st.secrets.get("TMDB_API_KEY", os.environ.get("TMDB_API_KEY", ""))
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", os.environ.get("OMDB_API_KEY", ""))

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


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
    # initial_sidebar_state="collapsed"
)

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

st.title("🎬 Movie Recommender System")
st.markdown("---")
st.markdown("### Find Your Next Favorite Movie 🍿")
st.markdown("")

@st.cache_resource
def load_data():
    """Load pickle files once and cache them"""
    movies_df = pickle.load(open("movies_df.pkl", "rb"))
    similarity_sparse = load_npz("similarity_mat.npz")
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
    .main {
        background-color: #A8DF8E;
    }
    .stButton > button {
        background-color: #4D2FB2;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Input section
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    user_selected_movie = st.selectbox(
        "🎥 Select a movie:",
        movies_titles,
        help="Choose a movie to get recommendations"
    )

with col3:
    recommend_btn = st.button("🎯 Recommend", use_container_width=True)

# Recommendations Display
if recommend_btn:
    names, posters = recommend(user_selected_movie)
    
    st.markdown("---")
    st.markdown("## 🌟 Top 5 Recommendations for You:")
    st.markdown("")
    
    cols = st.columns(5, gap="medium")

    for i in range(len(names)):
        with cols[i]:
            # Poster with border
            st.image(posters[i], width=300)
            
            # Movie name with styling
            st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 10px;
                    background: rgba(255, 107, 107, 0.2);
                    border-radius: 8px;
                    margin-top: 10px;
                ">
                    <p style="color: #FFD93D; font-weight: bold; margin: 0;">
                        {i+1}. {names[i][:25]}{'...' if len(names[i]) > 25 else ''}
                    </p>
                </div>
            """, unsafe_allow_html=True)
    