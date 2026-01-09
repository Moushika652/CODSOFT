from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os
from src.data_processing import load_data, prepare_features
from src.model_training import train_model, save_model, load_model

app = Flask(__name__, template_folder='templates', static_folder='static')

model = None
model_loaded = False
feature_columns = None
data_df = None
predictions_history = []

def initialize_model():
    global model, model_loaded, feature_columns, data_df
    
    model_path = 'models/sales_model.pkl'
    
    if os.path.exists('data/advertising.csv'):
        data_path = 'data/advertising.csv'
    elif os.path.exists('advertising.csv'):
        data_path = 'advertising.csv'
    elif os.path.exists('data/sales_data.csv'):
        data_path = 'data/sales_data.csv'
    else:
        print("No dataset found. Please ensure advertising.csv exists.")
        return False
    
    print(f"Loading dataset from: {data_path}")
    data_df = load_data(data_path)
    if data_df is None:
        return False
    
    print(f"Dataset loaded: {data_df.shape[0]} rows, {data_df.shape[1]} columns")
    print(f"Columns: {list(data_df.columns)}")
    
    X, y = prepare_features(data_df)
    if X is None or y is None:
        print("Error: Could not prepare features. Make sure 'Sales' column exists.")
        return False
    
    print(f"Features: {list(X.columns)}")
    
    if os.path.exists(model_path):
        try:
            model = load_model(model_path)
            feature_columns = X.columns.tolist()
            model_loaded = True
            print("Model loaded from file")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Training new model...")
    
    try:
        model, metrics, feature_columns = train_model(X, y)
        os.makedirs('models', exist_ok=True)
        save_model(model, model_path)
        print("Model trained and saved successfully")
        print(f"Training R²: {metrics['train']['r2']:.4f}")
        print(f"Test R²: {metrics['test']['r2']:.4f}")
        print(f"Test MAE: {metrics['test']['mae']:.4f}")
        model_loaded = True
        return True
    except Exception as e:
        print(f"Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/')
def index():
    return render_template('index.html', model_loaded=model_loaded)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if not model_loaded or model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please try again.'
            }), 500
        
        data = request.get_json()
        
        input_features = {}
        for col in feature_columns:
            value = data.get(col, 0)
            if value == 0:
                value = data.get(col.lower(), 0)
            if value == 0:
                value = data.get(col.lower().replace(' ', '_'), 0)
            try:
                input_features[col] = float(value)
            except (ValueError, TypeError):
                input_features[col] = 0.0
        
        input_array = np.array([[input_features[col] for col in feature_columns]])
        prediction = model.predict(input_array)[0]
        
        prediction = max(0, prediction)
        
        prediction_record = input_features.copy()
        prediction_record['Predicted_Sales'] = float(prediction)
        predictions_history.append(prediction_record)
        
        return jsonify({
            'success': True,
            'prediction': float(prediction),
            'features': input_features
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Prediction error: {error_details}")
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500
@app.route('/model-info', methods=['GET'])
def model_info():
    if not model_loaded or model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if data_df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    feature_info = []
    for col in feature_columns:
        if col in data_df.columns:
            feature_info.append({
                'name': col,
                'min': float(data_df[col].min()),
                'max': float(data_df[col].max()),
                'mean': float(data_df[col].mean())
            })
    
    return jsonify({
        'features': feature_columns,
        'feature_info': feature_info,
        'model_type': 'Linear Regression',
        'num_samples': len(data_df)
    })

@app.route('/download-predictions', methods=['GET'])
def download_predictions():
    global predictions_history
    if not predictions_history:
        return jsonify({'error': 'No predictions to download'}), 404
    
    try:
        df = pd.DataFrame(predictions_history)
        csv_string = df.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_string,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=sales_predictions.csv'}
        )
    except Exception as e:
        return jsonify({'error': f'Error creating download: {str(e)}'}), 500

@app.route('/exports')
def view_exports():
    global predictions_history
    return render_template('exports.html', predictions=predictions_history, count=len(predictions_history))

if __name__ == '__main__':
    print("Initializing Sales Prediction App...")
    if initialize_model():
        print("Model loaded successfully!")
        print("Starting Flask server...")
        print("Open your browser and go to: http://127.0.0.1:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize model. Please check your dataset.")
