from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import joblib
import numpy as np
import pandas as pd

# Initialize FastAPI app
app = FastAPI()

# Load trained models
rf_model = joblib.load("../ml_models/random_forest_model.joblib")
gb_model = joblib.load("../ml_models/gradient_boosting_model.joblib")

# Define input schema
class MovieInput(BaseModel):
    genres: List[str]
    director: str
    actors: List[str]
    runtime: int
    release_year: int
    vote_count: int

# Define output schema
class PredictionOutput(BaseModel):
    predicted_rating: float
    confidence_range: str
    top_influencing_features: List[str]

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "API is running"}

# Prediction endpoint
@app.post("/predict", response_model=PredictionOutput)
def predict_movie_rating(movie: MovieInput):
    # Prepare input features
    input_features = {
        "genres": ",".join(movie.genres),
        "director": movie.director,
        "actors": ",".join(movie.actors),
        "runtime": movie.runtime,
        "release_year": movie.release_year,
        "vote_count": movie.vote_count
    }

    # Convert input features to DataFrame
    input_df = pd.DataFrame([input_features])

    # Placeholder preprocessing (replace with actual preprocessing logic)
    processed_input = input_df  # Assume preprocessing is applied here

    # Make predictions
    rf_prediction = rf_model.predict(processed_input)[0]
    gb_prediction = gb_model.predict(processed_input)[0]

    # Combine predictions (example: average)
    predicted_rating = np.mean([rf_prediction, gb_prediction])
    confidence_range = f"{predicted_rating - 0.3:.1f} – {predicted_rating + 0.3:.1f}"

    top_influencing_features = [
        "Director Reputation",
        "Genre Alignment",
        "Cast Strength"
    ]

    return PredictionOutput(
        predicted_rating=predicted_rating,
        confidence_range=confidence_range,
        top_influencing_features=top_influencing_features
    )