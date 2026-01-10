from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import json
import uuid
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
from src.data_processing import load_data, prepare_features
from src.model_training import train_model, save_model, load_model

app = Flask(__name__, template_folder='templates', static_folder='static')

model = None
model_loaded = False
feature_columns = None
data_df = None
predictions_history = []
prediction_counter = 0
PREDICTIONS_FILE = 'data/sales_predictions_history.csv'

def load_predictions_history():
    global predictions_history
    if os.path.exists(PREDICTIONS_FILE):
        try:
            df = pd.read_csv(PREDICTIONS_FILE)
            predictions_history = df.to_dict('records')
            print(f"Loaded {len(predictions_history)} previous predictions from {PREDICTIONS_FILE}")
            return True
        except Exception as e:
            print(f"Error loading predictions history: {e}")
            predictions_history = []
            return False
    else:
        print("No previous predictions found. Starting fresh.")
        predictions_history = []
        return True

def save_predictions_history():
    global predictions_history, feature_columns
    try:
        os.makedirs('data', exist_ok=True)
        if predictions_history:
            df = pd.DataFrame(predictions_history)
            df.to_csv(PREDICTIONS_FILE, index=False)
            print(f"Saved {len(predictions_history)} predictions to {PREDICTIONS_FILE}")
        else:
            if feature_columns:
                columns = feature_columns.copy()
                columns.append('Predicted_Sales')
                df = pd.DataFrame(columns=columns)
                df.to_csv(PREDICTIONS_FILE, index=False)
            else:
                df = pd.DataFrame(columns=['TV', 'Radio', 'Newspaper', 'Predicted_Sales'])
                df.to_csv(PREDICTIONS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving predictions history: {e}")
        import traceback
        traceback.print_exc()
        return False

def initialize_model():
    global model, model_loaded, feature_columns, data_df
    
    model_path = 'models/sales_model.pkl'
    
    load_predictions_history()
    
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
        prediction_record['Timestamp'] = datetime.now().isoformat()
        prediction_record['Prediction_ID'] = f"PRED-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        global prediction_counter
        prediction_counter += 1
        prediction_record['Prediction_Number'] = prediction_counter
        predictions_history.append(prediction_record)
        
        save_predictions_history()
        
        return jsonify({
            'success': True,
            'prediction': float(prediction),
            'features': input_features,
            'currency_symbol': '₹',
            'timestamp': datetime.now().isoformat(),
            'prediction_id': f"PRED-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}",
            'prediction_number': prediction_counter
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
    try:
        load_predictions_history()
        
        if not predictions_history:
            if feature_columns:
                columns = feature_columns.copy()
                columns.append('Predicted_Sales')
                df = pd.DataFrame(columns=columns)
            else:
                df = pd.DataFrame(columns=['TV', 'Radio', 'Newspaper', 'Predicted_Sales'])
        else:
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

@app.route('/time-series-analysis', methods=['GET'])
def time_series_analysis():
    global predictions_history
    try:
        load_predictions_history()
        
        if len(predictions_history) < 5:
            return jsonify({
                'error': 'Insufficient data for time series analysis. Need at least 5 predictions.'
            }), 400
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(predictions_history)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values('Timestamp')
        
        # Basic statistics
        stats_data = {
            'total_predictions': len(df),
            'date_range': {
                'start': df['Timestamp'].min().isoformat(),
                'end': df['Timestamp'].max().isoformat()
            },
            'sales_stats': {
                'mean': float(df['Predicted_Sales'].mean()),
                'median': float(df['Predicted_Sales'].median()),
                'std': float(df['Predicted_Sales'].std()),
                'min': float(df['Predicted_Sales'].min()),
                'max': float(df['Predicted_Sales'].max())
            }
        }
        
        # Trend analysis
        df['days_ago'] = (datetime.now() - df['Timestamp']).dt.days
        X = df[['days_ago']].values
        y = df['Predicted_Sales'].values
        
        trend_model = LinearRegression()
        trend_model.fit(X, y)
        trend_slope = trend_model.coef_[0]
        trend_intercept = trend_model.intercept_
        
        # Determine trend direction
        if abs(trend_slope) < 0.01:
            trend_direction = 'stable'
        elif trend_slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
        
        # Seasonal patterns (simplified)
        df['hour'] = df['Timestamp'].dt.hour
        df['day_of_week'] = df['Timestamp'].dt.dayofweek
        df['month'] = df['Timestamp'].dt.month
        
        hourly_avg = df.groupby('hour')['Predicted_Sales'].mean().to_dict()
        daily_avg = df.groupby('day_of_week')['Predicted_Sales'].mean().to_dict()
        monthly_avg = df.groupby('month')['Predicted_Sales'].mean().to_dict()
        
        # Forecasting (simple linear extrapolation)
        future_days = 7
        future_dates = [datetime.now() + timedelta(days=i) for i in range(1, future_days + 1)]
        future_days_ago = [(datetime.now() - date).days for date in future_dates]
        
        future_predictions = trend_model.predict(np.array(future_days_ago).reshape(-1, 1))
        
        forecast_data = []
        for i, (date, pred) in enumerate(zip(future_dates, future_predictions)):
            forecast_data.append({
                'date': date.isoformat(),
                'predicted_sales': float(max(0, pred)),
                'confidence': max(0.1, 1 - (i * 0.1))  # Decreasing confidence
            })
        
        return jsonify({
            'statistics': stats_data,
            'trend_analysis': {
                'direction': trend_direction,
                'slope': float(trend_slope),
                'intercept': float(trend_intercept),
                'r_squared': float(trend_model.score(X, y))
            },
            'seasonal_patterns': {
                'hourly_average': hourly_avg,
                'daily_average': daily_avg,
                'monthly_average': monthly_avg
            },
            'forecast': forecast_data,
            'recent_predictions': df.tail(10).to_dict('records')
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Time series analysis error: {error_details}")
        return jsonify({'error': f'Analysis error: {str(e)}'}), 500

@app.route('/prediction-comparison', methods=['GET'])
def prediction_comparison():
    global predictions_history
    try:
        load_predictions_history()
        
        if len(predictions_history) < 2:
            return jsonify({
                'error': 'Insufficient data for comparison. Need at least 2 predictions.'
            }), 400
        
        df = pd.DataFrame(predictions_history)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.sort_values('Timestamp')
        
        # Calculate average
        avg_sales = df['Predicted_Sales'].mean()
        
        # Compare each prediction with average
        comparison_data = []
        for _, row in df.iterrows():
            prediction = row['Predicted_Sales']
            percentage_change = ((prediction - avg_sales) / avg_sales) * 100 if avg_sales != 0 else 0
            
            # Determine significance
            significance = 'normal'
            if abs(percentage_change) > 20:
                significance = 'significant'
            elif abs(percentage_change) > 10:
                significance = 'moderate'
            
            comparison_data.append({
                'prediction_id': row.get('Prediction_ID', 'N/A'),
                'prediction_number': row.get('Prediction_Number', 0),
                'timestamp': row['Timestamp'].isoformat(),
                'predicted_sales': float(prediction),
                'average_sales': float(avg_sales),
                'percentage_change': float(percentage_change),
                'significance': significance,
                'difference_from_average': float(prediction - avg_sales)
            })
        
        return jsonify({
            'comparison_data': comparison_data,
            'summary': {
                'total_predictions': len(df),
                'average_sales': float(avg_sales),
                'significant_predictions': len([x for x in comparison_data if x['significance'] == 'significant']),
                'highest_prediction': float(df['Predicted_Sales'].max()),
                'lowest_prediction': float(df['Predicted_Sales'].min())
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Prediction comparison error: {error_details}")
        return jsonify({'error': f'Comparison error: {str(e)}'}), 500

@app.route('/generate-pdf-report', methods=['GET'])
def generate_pdf_report():
    global predictions_history
    try:
        load_predictions_history()
        
        if len(predictions_history) < 2:
            return jsonify({
                'error': 'Insufficient data for PDF report. Need at least 2 predictions.'
            }), 400
        
        # Get time series data for charts
        time_series_response = None
        comparison_response = None
        
        try:
            # Get time series analysis
            ts_response = jsonify(time_series_analysis())
            if ts_response.status_code == 200:
                time_series_response = ts_response.get_json()
        except:
            pass
        
        try:
            # Get comparison data
            comp_response = jsonify(prediction_comparison())
            if comp_response.status_code == 200:
                comparison_response = comp_response.get_json()
        except:
            pass
        
        # Generate HTML content for PDF
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sales Prediction Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; color: #667eea; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
                .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; }}
                .chart-placeholder {{ background: #e9ecef; height: 200px; display: flex; align-items: center; justify-content: center; color: #6c757d; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #667eea; color: white; }}
                .footer {{ text-align: center; margin-top: 50px; color: #6c757d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Sales Prediction Analytics Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>📈 Executive Summary</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Total Predictions</h3>
                        <p>{len(predictions_history)}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Average Sales</h3>
                        <p>₹{sum(p['Predicted_Sales'] for p in predictions_history) / len(predictions_history):.2f}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Highest Prediction</h3>
                        <p>₹{max(p['Predicted_Sales'] for p in predictions_history):.2f}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Lowest Prediction</h3>
                        <p>₹{min(p['Predicted_Sales'] for p in predictions_history):.2f}</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Recent Predictions</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Prediction ID</th>
                            <th>Timestamp</th>
                            <th>Predicted Sales</th>
                            <th>TV</th>
                            <th>Radio</th>
                            <th>Newspaper</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add recent predictions (last 10)
        for pred in predictions_history[-10:]:
            html_content += f"""
                        <tr>
                            <td>{pred.get('Prediction_ID', 'N/A')}</td>
                            <td>{pred.get('Timestamp', 'N/A')}</td>
                            <td>₹{pred.get('Predicted_Sales', 0):.2f}</td>
                            <td>₹{pred.get('TV', 0):.2f}</td>
                            <td>₹{pred.get('Radio', 0):.2f}</td>
                            <td>₹{pred.get('Newspaper', 0):.2f}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📈 Trend Analysis</h2>
                <div class="chart-placeholder">
                    <p>📊 Sales Trend Chart (Interactive in Dashboard)</p>
                </div>
                <p><strong>Key Insights:</strong></p>
                <ul>
                    <li>Track your sales prediction trends over time</li>
                    <li>Identify patterns and seasonal variations</li>
                    <li>Compare performance across advertising channels</li>
                    <li>Monitor forecast accuracy and improvements</li>
                </ul>
            </div>
            
            <div class="footer">
                <p>Report generated by Sales Prediction System</p>
                <p>For detailed interactive charts and analysis, visit the dashboard</p>
            </div>
        </body>
        </html>
        """
        
        from flask import Response
        return Response(
            html_content,
            mimetype='text/html',
            headers={'Content-Disposition': 'attachment; filename=sales_prediction_report.html'}
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"PDF report generation error: {error_details}")
        return jsonify({'error': f'Report generation error: {str(e)}'}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/exports')
def view_exports():
    global predictions_history
    load_predictions_history()
    return render_template('exports.html', predictions=predictions_history, count=len(predictions_history), currency_symbol='₹')

if __name__ == '__main__':
    print("Initializing Sales Prediction App...")
    if initialize_model():
        print("Model loaded successfully!")
        print("Starting Flask server...")
        print("Server running on:")
        print("  - http://localhost:5000")
        print("  - http://0.0.0.0:5000")
        print("  - http://10.123.177.240:5000 (if accessible from network)")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize model. Please check your dataset.")
