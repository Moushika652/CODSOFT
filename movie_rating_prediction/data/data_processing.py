import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Load the dataset
def load_dataset(file_path):
    return pd.read_csv(file_path)

# Clean the dataset
def clean_dataset(df):
    # Drop duplicates
    df = df.drop_duplicates()

    # Handle missing values with intelligent defaults
    imputer = SimpleImputer(strategy='most_frequent')
    df['genres'] = imputer.fit_transform(df[['genres']])
    df['director'] = imputer.fit_transform(df[['director']])
    df['actors'] = imputer.fit_transform(df[['actors']])
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
    actor_ratings = df['actors'].str.split(',').explode().groupby(lambda x: x)['rating'].mean()

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