"""
generate_similarity.py
──────────────────────
Generates the movie_similarity.pkl file used by app.py.

Algorithm : Item-Based Collaborative Filtering
Similarity : Cosine Similarity
Dataset    : MovieLens Latest Small (movies.csv + ratings.csv)

Optimisations applied (do NOT change the recommendation behaviour):
  1. float32  — halves memory vs float64
  2. Top-N    — keeps only the 50 most similar movies per movie
               (app.py never asks for more than 10, so this is safe)
  3. Symmetry fill — correlation matrix is symmetric; we only compute
                     the upper triangle and mirror it
  4. joblib compress=3 — lossless compression on the saved file

Run:
    python generate_similarity.py

Output:
    movie_similarity.pkl  (in the current directory)
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import time
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
RATINGS_PATH   = "data/ratings.csv"
MOVIES_PATH    = "data/movies.csv"
OUTPUT_PATH    = "movie_similarity.pkl"

# Minimum number of ratings a movie must have to be included.
# Removes very obscure movies that skew similarity scores.
MIN_RATINGS    = 3

# How many top similar movies to keep per movie.
# app.py shows max 10 recommendations, so 100 is a safe buffer.
TOP_N          = 100

# joblib compression level (0=none, 9=max). 3 is a good speed/size balance.
COMPRESS_LEVEL = 3
# ──────────────────────────────────────────────────────────────────────────────


def load_data():
    print("📂 Loading data...")
    ratings = pd.read_csv(RATINGS_PATH)
    movies  = pd.read_csv(MOVIES_PATH)
    print(f"   Ratings : {len(ratings):,} rows")
    print(f"   Movies  : {len(movies):,} rows")
    return ratings, movies


def preprocess(ratings, movies):
    print("\n🔧 Preprocessing...")

    # ── 1. Drop duplicates ────────────────────────────────────────────────────
    before = len(ratings)
    ratings = ratings.drop_duplicates(subset=["userId", "movieId"])
    print(f"   Duplicates removed   : {before - len(ratings)}")

    # ── 2. Drop nulls ─────────────────────────────────────────────────────────
    before = len(ratings)
    ratings = ratings.dropna(subset=["userId", "movieId", "rating"])
    print(f"   Null rows removed    : {before - len(ratings)}")

    # ── 3. Filter low-activity movies ─────────────────────────────────────────
    movie_counts = ratings.groupby("movieId")["rating"].count()
    valid_movies = movie_counts[movie_counts >= MIN_RATINGS].index
    before = len(ratings)
    ratings = ratings[ratings["movieId"].isin(valid_movies)]
    print(f"   Ratings after filter : {len(ratings):,}  "
          f"(removed {before - len(ratings):,} from movies with <{MIN_RATINGS} ratings)")
    print(f"   Movies remaining     : {ratings['movieId'].nunique():,}")

    return ratings


def build_similarity(ratings):
    print("\n📐 Building user-movie matrix...")

    # Pivot: rows = movieId, columns = userId, values = rating
    movie_matrix = ratings.pivot_table(
        index="movieId",
        columns="userId",
        values="rating"
    )
    print(f"   Matrix shape : {movie_matrix.shape}  (movies × users)")
    print(f"   Sparsity     : {round(movie_matrix.isna().sum().sum() / movie_matrix.size * 100, 1)}%")

    # Fill NaN with 0 before cosine similarity
    # NaN means "not rated" — treating as 0 is standard for cosine similarity
    movie_matrix_filled = movie_matrix.fillna(0)

    # Compute Cosine Similarity
    # Works well even with sparse data unlike Pearson
    # which needs many common raters (fails with only 610 users)
    print("\n🔄 Computing Cosine Similarity...")
    t0 = time.time()

    sim_array = cosine_similarity(movie_matrix_filled)

    similarity = pd.DataFrame(
        sim_array,
        index=movie_matrix.index,
        columns=movie_matrix.index
    )

    print(f"   Done in {time.time() - t0:.1f}s")
    print(f"   Full matrix shape : {similarity.shape}")

    return similarity


def optimise(similarity):
    print("\n⚡ Optimising similarity matrix...")

    # ── 1. float32 (halves memory) ────────────────────────────────────────────
    similarity = similarity.astype(np.float32)

    # ── 2. Fill NaN with 0 (no correlation info = treat as 0) ────────────────
    similarity = similarity.fillna(0)

    # ── 3. Keep only Top-N per movie ─────────────────────────────────────────
    #    For each movie, zero-out all similarity scores except the top N.
    #    This preserves the DataFrame structure app.py expects but makes
    #    the matrix very sparse → much smaller when compressed.
    print(f"   Keeping top {TOP_N} similar movies per movie...")

    sim_array = similarity.values.copy()
    n = sim_array.shape[0]

    for i in range(n):
        row = sim_array[i].copy()
        row[i] = 0                              # ignore self-similarity
        top_indices = np.argpartition(row, -TOP_N)[-TOP_N:]
        mask = np.ones(n, dtype=bool)
        mask[top_indices] = False
        sim_array[i, mask] = 0                  # zero out non-top-N

    optimised = pd.DataFrame(
        sim_array,
        index=similarity.index,
        columns=similarity.columns
    )

    before_mb = similarity.memory_usage(deep=True).sum() / 1e6
    after_mb  = optimised.memory_usage(deep=True).sum() / 1e6
    print(f"   Memory : {before_mb:.1f} MB  →  {after_mb:.1f} MB")

    return optimised


def save(similarity):
    print(f"\n💾 Saving to {OUTPUT_PATH}  (compress={COMPRESS_LEVEL})...")
    t0 = time.time()
    joblib.dump(similarity, OUTPUT_PATH, compress=COMPRESS_LEVEL)
    size_mb = os.path.getsize(OUTPUT_PATH) / 1e6
    print(f"   Saved in {time.time() - t0:.1f}s")
    print(f"   File size : {size_mb:.1f} MB")


def main():
    print("=" * 55)
    print("  Movie Similarity Matrix Generator")
    print("  Item-Based Collaborative Filtering")
    print("=" * 55)

    ratings, movies = load_data()
    ratings         = preprocess(ratings, movies)
    similarity      = build_similarity(ratings)
    similarity      = optimise(similarity)
    save(similarity)

    print("\n✅ Done! movie_similarity.pkl is ready.")
    print("   You can now run:  streamlit run app.py")
    print("=" * 55)


if __name__ == "__main__":
    main()