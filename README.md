# 🎬 CineMatch — Movie Recommender System

A content-aware movie recommendation web app built with **item-based collaborative filtering** and a unique **decision fatigue** feature that adapts recommendations based on how long you've been browsing.

---

## 🚀 Demo

> Run locally using the steps below.

---

## 📌 Features

- 🎯 **Item-Based Collaborative Filtering** — recommends movies based on cosine similarity of user rating patterns
- 🧠 **Decision Fatigue Tracker** — reduces recommendation count over time to avoid choice overload
- 🔍 **Search & Genre Filter** — quickly find movies by title or filter by genre
- 🎴 **Movie Cards** — each recommendation shows genre tags, release year, and average rating
- ⚡ **Optimised Similarity Matrix** — precomputed and compressed for fast load times

---

## 🧠 How It Works

```
ratings.csv + movies.csv
        ↓
generate_similarity.py        ← preprocess data & compute similarity
        ↓
movie_similarity.pkl          ← precomputed cosine similarity matrix
        ↓
app.py                        ← Streamlit UI loads pkl and serves recommendations
```

### Algorithm
1. Raw ratings data is cleaned — duplicates removed, nulls dropped, low-activity movies filtered
2. A **user-movie matrix** is built (movies as rows, users as columns)
3. **Cosine similarity** is computed between every pair of movies
4. Only the **Top-100** most similar movies per movie are stored (app never needs more than 10)
5. Matrix is saved as a compressed pickle file using `joblib`

### Decision Fatigue Logic
| Time Spent | Fatigue Level | Recommendations Shown |
|---|---|---|
| 0 – 3 min | 🟢 Low | 10 |
| 3 – 5 min | 🟡 Medium | 5 |
| 5+ min | 🔴 High | 3 |

---

## 📂 Project Structure

```
movie-recommender-system/
│
├── data/
│   ├── movies.csv               ← movie titles and genres
│   └── ratings.csv              ← user ratings
│
├── app.py                       ← Streamlit web app
├── generate_similarity.py       ← builds movie_similarity.pkl from scratch
├── movie_similarity.pkl         ← precomputed similarity matrix
├── requirements.txt             ← dependencies
└── README.md
```

---

## 🗄️ Dataset

**MovieLens Latest Small** — [GroupLens Research, University of Minnesota](https://grouplens.org/datasets/movielens/)

| Property | Value |
|---|---|
| Movies | 9,742 |
| Ratings | 100,836 |
| Users | 610 |
| Rating Scale | 0.5 – 5.0 |
| Files Used | `movies.csv`, `ratings.csv` |

---

## ⚙️ Setup & Run

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/movie-recommender-system.git
cd movie-recommender-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate the similarity matrix
```bash
python generate_similarity.py
```
> This creates `movie_similarity.pkl` — only needs to be run once.

### 4. Launch the app
```bash
streamlit run app.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data manipulation |
| Scikit-learn | Cosine similarity |
| Joblib | Pickle serialization & compression |
| Streamlit | Web UI framework |
| HTML / CSS | Custom UI styling via `st.markdown()` |

---

## 📈 Preprocessing Steps

Inside `generate_similarity.py`:
- Remove duplicate ratings
- Drop null values
- Filter movies with fewer than 3 ratings
- Build user-movie pivot matrix
- Fill missing ratings with 0
- Compute cosine similarity
- Keep Top-100 similar movies per movie
- Save with joblib compression (level 3)

---

## 🙋 Author

N SRI VISHNU VARMA
[LinkedIn]www.linkedin.com/in/vishnuprabhas
[GitHub]https://github.com/Vishnu-Varma074
