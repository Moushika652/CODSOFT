import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Load the processed dataset
def load_processed_dataset(file_path):
    return pd.read_csv(file_path)

# Train and evaluate models
def train_and_evaluate(df):
    # Define features and target
    X = df.drop(columns=['rating'])
    y = df['rating']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize models
    rf = RandomForestRegressor(random_state=42)
    gb = GradientBoostingRegressor(random_state=42)

    # Hyperparameter tuning for Random Forest
    rf_params = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }
    rf_grid = GridSearchCV(rf, rf_params, cv=3, scoring='neg_mean_squared_error')
    rf_grid.fit(X_train, y_train)

    # Hyperparameter tuning for Gradient Boosting
    gb_params = {
        'n_estimators': [100, 200],
        'learning_rate': [0.05, 0.1],
        'max_depth': [3, 5]
    }
    gb_grid = GridSearchCV(gb, gb_params, cv=3, scoring='neg_mean_squared_error')
    gb_grid.fit(X_train, y_train)

    # Evaluate models
    models = {
        'Random Forest': rf_grid.best_estimator_,
        'Gradient Boosting': gb_grid.best_estimator_
    }

    for name, model in models.items():
        y_pred = model.predict(X_test)
        print(f"{name} Performance:")
        print(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
        print(f"RMSE: {mean_squared_error(y_test, y_pred, squared=False):.2f}")
        print(f"R2 Score: {r2_score(y_test, y_pred):.2f}\n")

    # Save the best models
    joblib.dump(rf_grid.best_estimator_, "random_forest_model.joblib")
    joblib.dump(gb_grid.best_estimator_, "gradient_boosting_model.joblib")

if __name__ == "__main__":
    # File path to the processed dataset
    file_path = "../data/processed_dataset.csv"

    # Load the dataset
    dataset = load_processed_dataset(file_path)

    # Train and evaluate models
    train_and_evaluate(dataset)
    print("Model training and evaluation completed.")