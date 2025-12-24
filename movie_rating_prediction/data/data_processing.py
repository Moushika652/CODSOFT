import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Load the dataset
def load_dataset(file_path):
    """
    Load the raw movies dataset from IMDb Movies India CSV and
    transform it into the schema expected by the ML pipeline:
    genres, director, actors, runtime, release_year, vote_count, rating.
    """
    # Handle common encoding issues
    try:
        raw_df = pd.read_csv(file_path)
    except UnicodeDecodeError:
        raw_df = pd.read_csv(file_path, encoding="latin1")

    # Standardize column names used by the rest of the pipeline
    df = raw_df.copy()

    # Map basic columns if present
    column_map = {
        "Genre": "genres",
        "Director": "director",
        "Rating": "rating",
    }
    for src, dest in column_map.items():
        if src in df.columns:
            df[dest] = df[src]

    # Combine actor columns into a single comma‑separated string
    actor_cols = [c for c in df.columns if c.lower().startswith("actor")]
    if actor_cols:
        df["actors"] = (
            df[actor_cols]
            .fillna("")
            .astype(str)
            .agg(", ".join, axis=1)
            .str.replace(r"(,\s*)+$", "", regex=True)
        )

    # Extract runtime in minutes from duration strings like "109 min"
    if "Duration" in df.columns:
        df["runtime"] = (
            df["Duration"]
            .astype(str)
            .str.extract(r"(\d+)", expand=False)
            .astype(float)
        )

    # Extract numeric year from strings like "(2019)"
    if "Year" in df.columns:
        df["release_year"] = (
            df["Year"]
            .astype(str)
            .str.extract(r"(\d{4})", expand=False)
            .astype(float)
        )

    # Votes to numeric vote_count (remove commas, handle missing)
    if "Votes" in df.columns:
        df["vote_count"] = (
            df["Votes"]
            .astype(str)
            .str.replace(",", "", regex=False)
        )
        df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce")

    # Keep only the columns required downstream (drop rows missing key fields later)
    expected_cols = [
        "genres",
        "director",
        "actors",
        "runtime",
        "release_year",
        "vote_count",
        "rating",
    ]
    # Some columns might still be missing; let cleaning handle NaNs but ensure they exist
    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA

    return df[expected_cols]

# Clean the dataset
def clean_dataset(df):
    # Drop duplicates
    df = df.drop_duplicates()

    # Handle missing values with intelligent defaults
    imputer = SimpleImputer(strategy='most_frequent')
    df['genres'] = imputer.fit_transform(df[['genres']]).ravel()
    df['director'] = imputer.fit_transform(df[['director']]).ravel()
    df['actors'] = imputer.fit_transform(df[['actors']]).ravel()
    df['runtime'] = df['runtime'].fillna(df['runtime'].median())
    df['release_year'] = df['release_year'].fillna(df['release_year'].median())
    df['vote_count'] = df['vote_count'].fillna(0)
    df['rating'] = df['rating'].fillna(df['rating'].mean())

    # Remove rows with invalid data
    df = df[df['runtime'] > 0]
    df = df[df['vote_count'] >= 0]
    df = df[df['release_year'] > 1900]

    return df

# Process the dataset
def process_dataset(df):
    # Encode genres as multi-label binary vectors
    unique_genres = set()
    df['genres'].str.split(',').apply(unique_genres.update)
    unique_genres = sorted(unique_genres)

    for genre in unique_genres:
        df[f'genre_{genre.strip()}'] = df['genres'].str.contains(genre, regex=False).astype(int)

    # Encode director and actors based on historical ratings
    director_ratings = df.groupby('director')['rating'].mean()

    # Build per-actor average rating
    actor_df = df[['actors', 'rating']].copy()
    actor_df['actors'] = actor_df['actors'].astype(str)
    actor_df = actor_df.assign(actor=actor_df['actors'].str.split(','))
    actor_df = actor_df.explode('actor')
    actor_df['actor'] = actor_df['actor'].str.strip()
    actor_ratings = actor_df.groupby('actor')['rating'].mean()

    df['director_score'] = df['director'].map(director_ratings)
    df['actors_score'] = df['actors'].apply(
        lambda x: np.mean([actor_ratings.get(actor.strip(), 0) for actor in x.split(',')])
    )

    # Normalize vote count using log normalization
    df['vote_count_normalized'] = np.log1p(df['vote_count'])

    # Scale release year using MinMaxScaler
    scaler = MinMaxScaler()
    df['release_year_scaled'] = scaler.fit_transform(df[['release_year']])

    # Advanced feature engineering: Interaction terms
    df['director_genre_interaction'] = df['director_score'] * df['genre_Drama']  # Example for Drama
    df['cast_genre_alignment'] = df['actors_score'] * df['genre_Action']  # Example for Action

    return df

if __name__ == "__main__":
    # File path to the dataset
    file_path = "../IMDb Movies India.csv"

    # Load, clean, and process the dataset
    dataset = load_dataset(file_path)
    cleaned_dataset = clean_dataset(dataset)
    processed_dataset = process_dataset(cleaned_dataset)

    # Save the processed dataset
    processed_dataset.to_csv("processed_dataset.csv", index=False)
    print("Dataset cleaned and processed successfully with advanced techniques.")