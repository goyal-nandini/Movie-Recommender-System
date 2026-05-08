# 🎬 Movie Recommender System

A professional **content-based movie recommendation app** built with **Streamlit** and **Python**. This project delivers an interactive web interface for discovering new movies using cosine similarity on movie metadata and dynamic poster fetching.

## 🌟 Live Demo
[Live Demo](https://movie-recommender-system-8fktkfpnvaa2nqqsszgez7.streamlit.app/)

## Screenshots
<img width="1905" height="728" alt="Screenshot 2026-05-08 223011" src="https://github.com/user-attachments/assets/690fb9b8-5ede-4110-872a-6f7c9b7bd8b1" />
<img width="1895" height="877" alt="Screenshot 2026-05-08 223057" src="https://github.com/user-attachments/assets/16df3ba6-1db8-4f75-b711-8bcfa9f111b7" />

---

## ✅ Project Overview
This app recommends the **top 5 movies** similar to a chosen film using a precomputed similarity matrix. It supports:
- movie search and selection
- random movie suggestions
- live poster display using TMDB and OMDb
- responsive recommendation cards with modern styling

## ✨ Key Features
- **Search-enabled movie selection** with live filtering
- **Random movie discovery** button for quick exploration
- **Recommendation engine** powered by cosine similarity
- **Poster fetching** from TMDB, with OMDb fallback and placeholder fallback
- **Cached API sessions and poster cache** for faster performance
- **Wide Streamlit layout** with custom CSS styling and animated card effects
- **Clear button** to reset selection and recommendations
- **Robust data loading** from `movies_df.pkl` and `similarity_mat.npz`

## 🧠 How It Works
1. The app loads preprocessed movie data from `movies_df.pkl`.
2. It loads a sparse similarity matrix from `similarity_mat.npz`.
3. When a movie is selected, the app retrieves the five most similar titles.
4. It fetches posters from the TMDB API, with OMDb fallback, and displays them in a polished card layout.

## 🧩 Tech Stack
- Python 3
- Streamlit
- SciPy
- Requests
- Pickle for serialized data
- TMDB API and OMDb API for posters

## 📦 Files Included
```bash
Movie-Recommender-System/
├── app.py                  # Streamlit application
├── movies_df.pkl           # Preprocessed movie metadata
├── similarity_mat.npz      # Precomputed sparse similarity matrix
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── tmdb_5000_credits.csv/  # Original credits data folder
│   └── tmdb_5000_credits.csv
└── tmdb_5000_movies.csv/   # Original movie data folder
    └── tmdb_5000_movies.csv
```

## 🚀 Installation
1. Clone the repository:
```bash
git clone https://github.com/goyal-nandini/Movie-Recommender-System.git
cd Movie-Recommender-System
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a secrets file for local API keys:
```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml <<SECRETS
TMDB_API_KEY = "your_tmdb_api_key"
OMDB_API_KEY = "your_omdb_api_key"
SECRETS
```
4. Run the app locally:
```bash
streamlit run app.py
```

## 🔐 Streamlit Secrets
The app uses the following secret keys:
- `TMDB_API_KEY` — required for TMDB poster images
- `OMDB_API_KEY` — used as a fallback if TMDB poster fetch fails

> If you deploy on Streamlit Cloud, add these keys under the app's **Settings → Secrets** section.

## 💡 Usage
- Type any movie name in the search box to find it quickly.
- Select a movie from the dropdown list.
- Click **Get Recommendations** to see the top 5 similar films.
- Click **Random Movie** to explore a random suggestion.
- Use **Clear** to reset the page and choose again.

## 📌 Notes
- If a poster cannot be fetched from TMDB or OMDb, the app displays a polished placeholder image.
- The app uses cached resources to speed up repeated requests and reduce API calls.

## 👩‍💻 Author
Nandini — Computer Science & Engineering Student, B.Tech '27
