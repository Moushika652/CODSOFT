from fastapi import FastAPI, UploadFile, HTTPException
import pandas as pd
import joblib
import os

app = FastAPI()

# Endpoint for dataset upload and auto-retraining
@app.post("/upload-dataset")
def upload_dataset(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Save the uploaded file
    file_location = f"uploaded_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())

    # Load the dataset
    try:
        new_data = pd.read_csv(file_location)
    except Exception as e:
        os.remove(file_location)
        raise HTTPException(status_code=400, detail=f"Error reading the file: {str(e)}")

    # Validate schema (example: check required columns)
    required_columns = ['genres', 'director', 'actors', 'runtime', 'release_year', 'vote_count', 'rating']
    if not all(col in new_data.columns for col in required_columns):
        os.remove(file_location)
        raise HTTPException(status_code=400, detail="Dataset does not match the required schema.")

    # Retrain models (placeholder logic)
    retrain_models(new_data)

    # Remove the uploaded file
    os.remove(file_location)

    return {"detail": "Dataset uploaded and models retrained successfully."}

# Placeholder function for retraining models
def retrain_models(new_data):
    # Combine new data with existing data
    existing_data = pd.read_csv("../data/processed_dataset.csv")
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)

    # Save the combined dataset
    combined_data.to_csv("../data/processed_dataset.csv", index=False)

    # Retrain models (reuse training logic)
    from train_and_evaluate import train_and_evaluate
    train_and_evaluate(combined_data)

# Endpoint for explainable AI insights
@app.get("/explain-prediction")
def explain_prediction():
    # Placeholder for SHAP or similar explainability logic
    return {"detail": "Explainable AI insights will be implemented here."}