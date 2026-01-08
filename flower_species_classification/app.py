from flask import Flask, request, jsonify, render_template
import numpy as np
import joblib
import os
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

app = Flask(__name__, template_folder='templates', static_folder='static')

model = None
model_path = 'models/iris_model.pkl'
species_names = ['Iris Setosa', 'Iris Versicolor', 'Iris Virginica']


def train_model():
    global model
    
    iris = load_iris()
    X = iris.data
    y = iris.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model trained successfully!")
    print(f"Accuracy: {accuracy:.4f}")
    
    os.makedirs('models', exist_ok=True)
    
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")
    
    return model


def load_model():
    global model
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")
        return True
    return False


def initialize_model():
    if not load_model():
        train_model()
    return model


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        sepal_length = float(data.get('sepal_length', 0))
        sepal_width = float(data.get('sepal_width', 0))
        petal_length = float(data.get('petal_length', 0))
        petal_width = float(data.get('petal_width', 0))
        
        if any(val <= 0 for val in [sepal_length, sepal_width, petal_length, petal_width]):
            return jsonify({
                'error': 'All measurements must be positive numbers'
            }), 400
        
        features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        predicted_species = species_names[prediction]
        confidence = float(probabilities[prediction] * 100)
        
        probabilities_dict = {
            species_names[i]: float(prob * 100) 
            for i, prob in enumerate(probabilities)
        }
        
        return jsonify({
            'success': True,
            'prediction': predicted_species,
            'confidence': confidence,
            'probabilities': probabilities_dict,
            'species_id': int(prediction)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Prediction error: {str(e)}'
        }), 500


@app.route('/model-info', methods=['GET'])
def model_info():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    iris = load_iris()
    
    return jsonify({
        'species': species_names,
        'features': ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width'],
        'feature_description': {
            'Sepal Length': 'Length of the sepal (cm)',
            'Sepal Width': 'Width of the sepal (cm)',
            'Petal Length': 'Length of the petal (cm)',
            'Petal Width': 'Width of the petal (cm)'
        },
        'num_samples': len(iris.data),
        'model_type': 'Random Forest Classifier'
    })


if __name__ == '__main__':
    initialize_model()
    print("Starting Flask application...")
    app.run(debug=True, host='0.0.0.0', port=5000)

