from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from src.data_loading import load_csv
from src.feature_engineering import add_features

app = Flask(__name__, template_folder='templates')

predictor = None
model_loaded = False


class MovieRatingPredictor:
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.model_columns = None
        self.model_path = 'models/final_model.pkl'
        self.encoders_path = 'models/label_encoders.pkl'
        self.columns_path = 'models/model_columns.pkl'
        
    def train_model_if_needed(self):
        if os.path.exists(self.model_path) and os.path.exists(self.encoders_path):
            return self.load_model()
        else:
            return self.train_new_model()
    
    def train_new_model(self):
        try:
            df = load_csv('data/processed/cleaned_movie_dataset.csv')
            
            if df is None:
                return False
            
            feature_cols = [col for col in df.columns if col != 'Rating']
            X = df[feature_cols].copy()
            y = df['Rating'].copy()
            
            X = X.fillna('Unknown')
            
            categorical_cols = X.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le
            
            os.makedirs('models', exist_ok=True)
            joblib.dump(self.label_encoders, self.encoders_path)
            
            X = add_features(X)
            
            self.model_columns = list(X.columns)
            joblib.dump(self.model_columns, self.columns_path)
            
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            self.model = LinearRegression()
            self.model.fit(X_train, y_train)
            
            joblib.dump(self.model, self.model_path)
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.label_encoders = joblib.load(self.encoders_path)
            self.model_columns = joblib.load(self.columns_path)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def preprocess_input(self, movie_name, genre, actor, votes):
        try:
            input_data = {
                'Name': [movie_name],
                'Genre': [genre],
                'Actor 1': [actor],
                'Votes': [votes]
            }
            
            df = load_csv('data/processed/cleaned_movie_dataset.csv')
            if df is None:
                return None
            
            feature_cols = [col for col in df.columns if col != 'Rating']
            
            input_row = {}
            for col in feature_cols:
                if col in input_data:
                    input_row[col] = input_data[col][0]
                elif col in ['Actor 2', 'Actor 3']:
                    input_row[col] = 'Unknown'
                elif col == 'Year':
                    input_row[col] = 2020
                elif col == 'Duration':
                    input_row[col] = 120
                elif col == 'Director':
                    input_row[col] = 'Unknown'
                else:
                    input_row[col] = 0
            
            input_df = pd.DataFrame([input_row])
            
            categorical_cols = input_df.select_dtypes(include=['object']).columns
            
            for col in categorical_cols:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    try:
                        input_df[col] = le.transform(input_df[col].astype(str))
                    except ValueError:
                        if len(le.classes_) > 0:
                            default_value = le.transform([le.classes_[0]])[0]
                            input_df[col] = default_value
                        else:
                            input_df[col] = 0
                else:
                    input_df[col] = 0
            
            for col in self.model_columns:
                if col not in input_df.columns:
                    input_df[col] = 0
            
            input_df = input_df[self.model_columns]
            
            return input_df
            
        except Exception as e:
            import traceback
            print(f"Error preprocessing input: {e}")
            traceback.print_exc()
            return None
    
    def predict(self, movie_name, genre, actor, votes):
        if self.model is None:
            print("Model is None")
            return None
        
        input_df = self.preprocess_input(movie_name, genre, actor, votes)
        
        if input_df is None:
            print("Preprocessing returned None")
            return None
        
        try:
            if list(input_df.columns) != self.model_columns:
                print(f"Column mismatch! Input: {list(input_df.columns)}, Model: {self.model_columns}")
                input_df = input_df[self.model_columns]
            
            prediction = self.model.predict(input_df)[0]
            prediction = max(0, min(10, prediction))
            return round(prediction, 2)
        except Exception as e:
            print(f"Error making prediction: {e}")
            import traceback
            traceback.print_exc()
            return None


def initialize_predictor():
    global predictor, model_loaded
    predictor = MovieRatingPredictor()
    model_loaded = predictor.train_model_if_needed()
    return model_loaded


@app.route('/')
def home():
    return render_template('index.html', model_loaded=model_loaded)


@app.route('/search_movie', methods=['POST'])
def search_movie():
    try:
        data = request.get_json()
        movie_name = data.get('movie_name', '').strip()
        
        if not movie_name:
            return jsonify({
                'success': False,
                'error': 'Please provide a movie name.'
            }), 400
        
        df = load_csv('data/processed/cleaned_movie_dataset.csv')
        if df is None:
            return jsonify({
                'success': False,
                'error': 'Could not load movie database.'
            }), 500
        
        search_terms = [term.strip() for term in movie_name.lower().split() if term.strip()]
        
        if not search_terms:
            return jsonify({
                'success': False,
                'error': 'Please provide a search term.'
            }), 400
        
        mask = pd.Series([False] * len(df))
        
        for term in search_terms:
            name_match = df['Name'].str.contains(term, case=False, na=False, regex=False)
            genre_match = df['Genre'].astype(str).str.contains(term, case=False, na=False, regex=False)
            actor1_match = df['Actor 1'].astype(str).str.contains(term, case=False, na=False, regex=False)
            actor2_match = df['Actor 2'].astype(str).str.contains(term, case=False, na=False, regex=False)
            actor3_match = df['Actor 3'].astype(str).str.contains(term, case=False, na=False, regex=False)
            director_match = df['Director'].astype(str).str.contains(term, case=False, na=False, regex=False)
            
            term_mask = name_match | genre_match | actor1_match | actor2_match | actor3_match | director_match
            mask = mask | term_mask
        
        search_results = df[mask]
        
        if not search_results.empty:
            search_results = search_results.copy()
            search_results['relevance'] = search_results['Name'].str.contains(
                movie_name, case=False, na=False, regex=False
            ).astype(int)
            search_results = search_results.sort_values(
                by=['relevance', 'Rating'], 
                ascending=[False, False]
            ).drop('relevance', axis=1)
        
        if search_results.empty:
            return jsonify({
                'success': False,
                'error': f'No movies found matching "{movie_name}". Try a different search term.'
            }), 404
        
        movies = []
        search_lower = movie_name.lower()
        for _, row in search_results.head(20).iterrows():
            matched_in = []
            name_lower = str(row['Name']).lower()
            genre_lower = str(row['Genre']).lower() if pd.notna(row['Genre']) else ''
            actor1_lower = str(row['Actor 1']).lower() if pd.notna(row['Actor 1']) else ''
            director_lower = str(row['Director']).lower() if pd.notna(row['Director']) else ''
            
            for term in search_terms:
                if term in name_lower:
                    matched_in.append('Name')
                if term in genre_lower:
                    matched_in.append('Genre')
                if term in actor1_lower:
                    matched_in.append('Actor')
                if term in director_lower:
                    matched_in.append('Director')
            
            matched_in = list(set(matched_in))
            
            movies.append({
                'name': row['Name'],
                'rating': float(row['Rating']) if pd.notna(row['Rating']) else None,
                'genre': row['Genre'] if pd.notna(row['Genre']) else 'N/A',
                'year': int(row['Year']) if pd.notna(row['Year']) else None,
                'votes': int(row['Votes']) if pd.notna(row['Votes']) else None,
                'director': row['Director'] if pd.notna(row['Director']) else 'N/A',
                'actor1': row['Actor 1'] if pd.notna(row['Actor 1']) else 'N/A',
                'matched_in': ', '.join(matched_in) if matched_in else 'Name'
            })
        
        return jsonify({
            'success': True,
            'movies': movies,
            'count': len(movies)
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500


@app.route('/predict_rating', methods=['POST'])
def predict_rating():
    try:
        data = request.get_json()
        
        movie_name = data.get('movie_name', '').strip()
        genre = data.get('genre', '').strip()
        actor = data.get('actor', '').strip()
        votes = data.get('votes', '')
        
        if not movie_name or not genre or not actor:
            return jsonify({
                'success': False,
                'error': 'Please provide movie name, genre, and actor.'
            }), 400
        
        try:
            votes = int(votes)
            if votes < 0:
                return jsonify({
                    'success': False,
                    'error': 'Votes must be a positive number.'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Votes must be a valid number.'
            }), 400
        
        if not model_loaded or predictor.model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please try again in a moment.'
            }), 500
        
        try:
            predicted_rating = predictor.predict(movie_name, genre, actor, votes)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Prediction error: {error_details}")
            return jsonify({
                'success': False,
                'error': f'Prediction failed: {str(e)}'
            }), 500
        
        if predicted_rating is None:
            return jsonify({
                'success': False,
                'error': 'Failed to make prediction. Please check your inputs and ensure the model is properly loaded.'
            }), 500
        
        return jsonify({
            'success': True,
            'predicted_rating': predicted_rating,
            'movie_name': movie_name,
            'genre': genre,
            'actor': actor,
            'votes': votes
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("Initializing Movie Rating Prediction App...")
    if initialize_predictor():
        print("Model loaded successfully!")
        print("Starting Flask server...")
        print("Open your browser and go to: http://127.0.0.1:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize model. Please check your dataset.")

