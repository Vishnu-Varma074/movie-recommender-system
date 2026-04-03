# import streamlit as st
# import pandas as pd
# import joblib
# import time

# st.set_page_config(layout="wide")

# # -----------------------------
# # LOAD DATA
# # -----------------------------
# @st.cache_data
# def load_data():
#     ratings = pd.read_csv("data/ratings.csv")
#     movies = pd.read_csv("data/movies.csv")
#     return ratings, movies

# ratings, movies = load_data()

# # -----------------------------
# # LOAD PRECOMPUTED SIMILARITY
# # -----------------------------
# @st.cache_resource
# def load_similarity():
#     similarity_df = joblib.load("movie_similarity.pkl")
#     return similarity_df

# movie_similarity_df = load_similarity()

# # -----------------------------
# # SESSION TIMER
# # -----------------------------
# if "start_time" not in st.session_state:
#     st.session_state.start_time = time.time()

# elapsed_time_seconds = int(time.time() - st.session_state.start_time)

# # Convert to MM:SS format
# minutes = elapsed_time_seconds // 60
# seconds = elapsed_time_seconds % 60
# formatted_time = f"{minutes:02d}:{seconds:02d}"

# # -----------------------------
# # FATIGUE + DYNAMIC RECOMMENDATIONS
# # -----------------------------
# if minutes < 3:
#     fatigue_level = "Low"
#     fatigue_score = 20
#     num_recommendations = 10
# elif 3 <= minutes < 5:
#     fatigue_level = "Medium"
#     fatigue_score = 60
#     num_recommendations = 5
# else:
#     fatigue_level = "High"
#     fatigue_score = 90
#     num_recommendations = 3

# # -----------------------------
# # TOP DISPLAY BAR
# # -----------------------------
# col1, col2 = st.columns([1, 3])

# with col1:
#     st.metric("⏱ Time Spent", formatted_time)

# with col2:
#     st.write("### 🧠 Decision Fatigue Level")
#     st.progress(fatigue_score)
#     st.write(f"**Status:** {fatigue_level}")

# st.markdown("---")

# # -----------------------------
# # MOVIE SELECTION
# # -----------------------------
# st.header("🎬 Movie Recommendation System")

# movie_list = movies['title'].values
# selected_movie = st.selectbox("Choose a movie:", movie_list)

# # -----------------------------
# # RECOMMEND FUNCTION
# # -----------------------------
# def recommend(movie_title, num_recommendations):
#     movie_id = movies[movies['title'] == movie_title]['movieId'].values[0]

#     similar_movies = movie_similarity_df[movie_id] \
#         .sort_values(ascending=False)[1:num_recommendations+1]

#     recommended_titles = movies[
#         movies['movieId'].isin(similar_movies.index)
#     ]['title']

#     return recommended_titles.values

# # -----------------------------
# # DISPLAY RECOMMENDATIONS
# # -----------------------------
# if selected_movie:
#     st.subheader(f"Recommended Movies ({num_recommendations} shown)")

#     recommendations = recommend(selected_movie, num_recommendations)

#     for i, movie in enumerate(recommendations, 1):
#         st.write(f"{i}. {movie}")


import streamlit as st
import pandas as pd
import joblib
import time

st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #f0f0f0;
}

/* Hide default streamlit elements */
#MainMenu, footer, header {visibility: hidden;}
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── HERO TITLE ── */
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 4rem;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #e50914 0%, #ff6b35 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    line-height: 1;
}
.hero-sub {
    font-size: 0.9rem;
    color: #888;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
    margin-bottom: 1.5rem;
}

/* ── FATIGUE BAR ── */
.fatigue-container {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
.fatigue-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #666;
    margin-bottom: 6px;
}
.fatigue-row {
    display: flex;
    align-items: center;
    gap: 12px;
}
.fatigue-time {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #e50914;
    min-width: 70px;
}
.fatigue-track {
    flex: 1;
    height: 6px;
    background: #2a2a2a;
    border-radius: 99px;
    overflow: hidden;
}
.fatigue-fill-low    { height: 100%; background: #22c55e; border-radius: 99px; transition: width 1s ease; }
.fatigue-fill-medium { height: 100%; background: #f59e0b; border-radius: 99px; transition: width 1s ease; }
.fatigue-fill-high   { height: 100%; background: #e50914; border-radius: 99px; transition: width 1s ease; }
.fatigue-status {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    min-width: 60px;
    text-align: right;
}

/* ── MOVIE CARD ── */
.movie-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
}
.movie-card:hover {
    border-color: #e50914;
    transform: translateX(4px);
}
.movie-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #e50914, #ff6b35);
    border-radius: 99px;
}
.movie-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    color: #333;
    min-width: 40px;
    text-align: center;
}
.movie-info { flex: 1; }
.movie-title-card {
    font-size: 1rem;
    font-weight: 600;
    color: #f0f0f0;
    margin-bottom: 4px;
    line-height: 1.3;
}
.movie-genre-tag {
    display: inline-block;
    background: #2a2a2a;
    color: #aaa;
    font-size: 0.68rem;
    padding: 2px 8px;
    border-radius: 99px;
    margin-right: 4px;
    margin-top: 2px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.movie-year {
    font-size: 0.75rem;
    color: #555;
    margin-top: 4px;
}

/* ── SELECTED MOVIE BANNER ── */
.selected-banner {
    background: linear-gradient(135deg, #1a0a0a, #1a1a1a);
    border: 1px solid #e50914;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
}
.selected-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #e50914;
    margin-bottom: 2px;
}
.selected-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    color: #f0f0f0;
    letter-spacing: 1px;
}

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #555;
    margin-bottom: 1rem;
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #2a2a2a;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid #1e1e1e;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stTextInput label {
    color: #888 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

/* ── INPUTS ── */
.stSelectbox > div > div,
.stTextInput > div > div > input,
.stMultiSelect > div > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #f0f0f0 !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: #e50914 !important;
    box-shadow: 0 0 0 2px rgba(229,9,20,0.15) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 0.8rem 1rem;
}
[data-testid="stMetricLabel"] { color: #666 !important; font-size: 0.7rem !important; }
[data-testid="stMetricValue"] { color: #f0f0f0 !important; }

/* ── EMPTY STATE ── */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #444;
}
.empty-state-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.empty-state-text { font-size: 0.9rem; }

/* ── BADGE ── */
.count-badge {
    display: inline-block;
    background: #e50914;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 99px;
    margin-left: 8px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    ratings = pd.read_csv("data/ratings.csv")
    movies  = pd.read_csv("data/movies.csv")
    # Precompute avg rating per movie
    avg_ratings = ratings.groupby("movieId")["rating"].agg(["mean", "count"]).reset_index()
    avg_ratings.columns = ["movieId", "avg_rating", "num_ratings"]
    movies = movies.merge(avg_ratings, on="movieId", how="left")
    # Extract year from title
    movies["year"] = movies["title"].str.extract(r'\((\d{4})\)$')
    return ratings, movies

@st.cache_resource
def load_similarity():
    return joblib.load("movie_similarity.pkl")

ratings, movies = load_data()
movie_similarity_df = load_similarity()

# All genres
all_genres = sorted(set(
    g for genres in movies["genres"] for g in genres.split("|")
    if g != "(no genres listed)"
))


# ─────────────────────────────────────────
# SESSION TIMER
# ─────────────────────────────────────────
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

elapsed   = int(time.time() - st.session_state.start_time)
minutes   = elapsed // 60
seconds   = elapsed % 60
fmt_time  = f"{minutes:02d}:{seconds:02d}"

if minutes < 3:
    fatigue_level = "Low"
    fatigue_pct   = int((elapsed / 180) * 40)
    fatigue_class = "fatigue-fill-low"
    num_recs      = 10
elif minutes < 5:
    fatigue_level = "Medium"
    fatigue_pct   = 40 + int(((elapsed - 180) / 120) * 35)
    fatigue_class = "fatigue-fill-medium"
    num_recs      = 5
else:
    fatigue_level = "High"
    fatigue_pct   = min(100, 75 + int((elapsed - 300) / 60) * 5)
    fatigue_class = "fatigue-fill-high"
    num_recs      = 3


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='margin-bottom:1.5rem;'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:2rem;
                        background:linear-gradient(135deg,#e50914,#ff6b35);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                        letter-spacing:3px;'>CineMatch</div>
            <div style='font-size:0.7rem;color:#555;letter-spacing:2px;text-transform:uppercase;'>
                AI Movie Recommender
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Search
    search_query = st.text_input("🔍 Search Movie", placeholder="e.g. Toy Story...")

    # Genre filter
    selected_genres = st.multiselect(
        "🎭 Filter by Genre",
        options=all_genres,
        default=[]
    )

    st.markdown("---")

    st.markdown("<div style='font-size:0.65rem;color:#333;text-align:center;'>MovieLens Latest Small Dataset<br>GroupLens Research, U of Minnesota</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────

# Hero
st.markdown("""
    <div class='hero-title'>CineMatch</div>
    <div class='hero-sub'>Item-Based Collaborative Filtering · MovieLens Dataset</div>
""", unsafe_allow_html=True)

# Fatigue Bar
st.markdown(f"""
<div class='fatigue-container'>
    <div class='fatigue-label'>Decision Fatigue Tracker</div>
    <div class='fatigue-row'>
        <div class='fatigue-time'>⏱ {fmt_time}</div>
        <div class='fatigue-track'>
            <div class='{fatigue_class}' style='width:{fatigue_pct}%;'></div>
        </div>
        <div class='fatigue-status' style='color:{"#22c55e" if fatigue_level=="Low" else "#f59e0b" if fatigue_level=="Medium" else "#e50914"};'>
            {fatigue_level}
        </div>
    </div>
    <div style='font-size:0.72rem;color:#555;margin-top:6px;'>
        Showing <strong style='color:#f0f0f0;'>{num_recs} recommendations</strong> based on your browsing time
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# FILTER MOVIES
# ─────────────────────────────────────────
filtered_movies = movies.copy()

if selected_genres:
    mask = filtered_movies["genres"].apply(
        lambda g: any(genre in g.split("|") for genre in selected_genres)
    )
    filtered_movies = filtered_movies[mask]

if search_query:
    filtered_movies = filtered_movies[
        filtered_movies["title"].str.contains(search_query, case=False, na=False)
    ]

movie_list = filtered_movies["title"].values

# Movie selector
st.markdown(f"<div class='section-header'>Select a Movie <span class='count-badge'>{len(movie_list):,} available</span></div>", unsafe_allow_html=True)

if len(movie_list) == 0:
    st.markdown("""
        <div class='empty-state'>
            <div class='empty-state-icon'>🎭</div>
            <div class='empty-state-text'>No movies match your filters. Try adjusting your search or genre selection.</div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

selected_movie = st.selectbox("Select a Movie", movie_list, label_visibility="collapsed")


# ─────────────────────────────────────────
# RECOMMEND FUNCTION
# ─────────────────────────────────────────
def recommend(movie_title, n):
    movie_id = movies[movies["title"] == movie_title]["movieId"].values[0]

    # Check if movie exists in similarity matrix
    if movie_id not in movie_similarity_df.columns:
        return None

    similar  = movie_similarity_df[movie_id].sort_values(ascending=False)[1:n+1]
    # Filter out zero similarity scores (unrated combinations)
    similar  = similar[similar > 0]
    recs     = movies[movies["movieId"].isin(similar.index)].copy()
    recs["similarity"] = recs["movieId"].map(similar)
    recs = recs.sort_values("similarity", ascending=False)
    return recs


# ─────────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────────
if selected_movie:
    # Selected movie banner
    sel_row   = movies[movies["title"] == selected_movie].iloc[0]
    sel_year  = sel_row["year"] if pd.notna(sel_row.get("year")) else ""
    sel_genre = sel_row["genres"].replace("|", " · ")
    sel_avg   = f"{sel_row['avg_rating']:.1f} ⭐" if pd.notna(sel_row.get("avg_rating")) else ""

    st.markdown(f"""
    <div class='selected-banner'>
        <div style='font-size:2rem;'>🎬</div>
        <div>
            <div class='selected-label'>Now Finding Similar To</div>
            <div class='selected-title'>{selected_movie}</div>
            <div style='font-size:0.75rem;color:#666;margin-top:2px;'>{sel_genre} &nbsp;·&nbsp; {sel_year} &nbsp;·&nbsp; {sel_avg}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recommendations
    st.markdown(f"<div class='section-header'>Top {num_recs} Recommendations</div>", unsafe_allow_html=True)

    try:
        recs = recommend(selected_movie, num_recs)

        if recs is None or len(recs) == 0:
            st.warning("⚠️ This movie has too few ratings to generate recommendations. Try another movie.")
        else:
            for i, (_, row) in enumerate(recs.iterrows(), 1):
                title    = row["title"]
                genres   = row["genres"].split("|")
                year     = row["year"] if pd.notna(row.get("year")) else ""
                avg_r    = f"{row['avg_rating']:.1f} ⭐ ({int(row['num_ratings'])} ratings)" if pd.notna(row.get("avg_rating")) else ""

                genre_tags = "".join(
                    f"<span class='movie-genre-tag'>{g}</span>"
                    for g in genres if g != "(no genres listed)"
                )

                st.markdown(f"""
                <div class='movie-card'>
                    <div class='movie-rank'>#{i}</div>
                    <div class='movie-info'>
                        <div class='movie-title-card'>{title}</div>
                        <div>{genre_tags}</div>
                        <div class='movie-year'>{year} &nbsp; {avg_r}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Could not generate recommendations: {e}")