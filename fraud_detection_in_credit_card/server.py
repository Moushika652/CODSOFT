#!/usr/bin/env python3
"""
Credit Card Fraud Detection Web Server
====================================

A Flask web server to serve the fraud detection application with API endpoints
for real-time transaction analysis and fraud detection.

Author: ML Developer
Date: 2024
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import random
import datetime
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

app = Flask(__name__)
CORS(app)

# Global storage for transactions and statistics
transactions_history = []
statistics = {
    'total': 0,
    'fraud': 0,
    'legitimate': 0,
    'detection_rate': 0.0
}

@dataclass
class Transaction:
    """Transaction data structure"""
    card_number: str
    amount: float
    merchant: str
    location: str
    time: str
    transaction_type: str
    is_fraud: bool
    risk_score: int
    timestamp: str

class FraudDetectionEngine:
    """Advanced fraud detection engine with ML-inspired logic"""
    
    def __init__(self):
        self.merchant_risk_scores = {
            'amazon': 5,
            'walmart': 3,
            'target': 4,
            'bestbuy': 6,
            'unknown': 25
        }
        
        self.location_risk_scores = {
            'online': 10,
            'local': 0,
            'domestic': 15,
            'international': 35
        }
        
        self.type_risk_scores = {
            'purchase': 0,
            'withdrawal': 15,
            'transfer': 10,
            'refund': 5
        }
    
    def calculate_risk_scores(self, amount: float, merchant: str, 
                            location: str, time: str, transaction_type: str) -> Dict:
        """Calculate comprehensive risk scores for a transaction"""
        
        # Amount risk calculation
        amount_risk = 0
        if amount > 1000:
            amount_risk = min(30, (amount / 100) * 3)
        elif amount > 500:
            amount_risk = 15
        elif amount > 100:
            amount_risk = 5
        
        # Location risk calculation
        location_risk = self.location_risk_scores.get(location, 10)
        
        # Time risk calculation
        time_risk = 0
        try:
            hour = int(time.split(':')[0])
            if hour >= 22 or hour <= 5:
                time_risk = 20
            elif hour >= 18 or hour <= 7:
                time_risk = 10
        except:
            time_risk = 5
        
        # Pattern risk calculation
        pattern_risk = self.merchant_risk_scores.get(merchant, 15)
        pattern_risk += self.type_risk_scores.get(transaction_type, 5)
        
        # Add some randomness for realistic simulation
        pattern_risk += random.uniform(0, 10)
        
        # Calculate total risk
        total_risk = min(100, amount_risk + location_risk + time_risk + pattern_risk)
        
        return {
            'amount_risk': round(amount_risk),
            'location_risk': round(location_risk),
            'time_risk': round(time_risk),
            'pattern_risk': round(pattern_risk),
            'total_risk': round(total_risk)
        }
    
    def detect_fraud(self, risk_scores: Dict) -> Tuple[bool, str]:
        """Determine if transaction is fraudulent based on risk scores"""
        total_risk = risk_scores['total_risk']
        
        # Advanced fraud detection logic
        if total_risk > 70:
            return True, "High risk - Multiple suspicious factors detected"
        elif total_risk > 50:
            return True, "Medium risk - Unusual transaction pattern"
        elif total_risk > 30:
            return False, "Low risk - Minor anomalies detected"
        else:
            return False, "Very low risk - Normal transaction pattern"

# Initialize fraud detection engine
fraud_engine = FraudDetectionEngine()

def mask_card_number(card_number: str) -> str:
    """Mask card number showing only last 4 digits"""
    if not card_number:
        return '**** **** **** ****'
    
    # Remove any non-digit characters
    clean_number = re.sub(r'\D', '', card_number)
    
    if len(clean_number) < 4:
        return '**** **** **** ****'
    
    # Show only last 4 digits
    last_four = clean_number[-4:]
    return f'**** **** **** {last_four}'

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/analyze_transaction', methods=['POST'])
def analyze_transaction():
    """API endpoint to analyze a transaction for fraud"""
    
    try:
        data = request.get_json()
        
        # Extract transaction data
        card_number = mask_card_number(data.get('cardNumber', ''))
        amount = float(data.get('amount', 0))
        merchant = data.get('merchant', '')
        location = data.get('location', '')
        time = data.get('time', '')
        transaction_type = data.get('transactionType', '')
        
        # Validate required fields
        if not all([amount, merchant, location, time, transaction_type]):
            return jsonify({
                'success': False,
                'error': 'Missing required transaction details'
            }), 400
        
        # Calculate risk scores
        risk_analysis = fraud_engine.calculate_risk_scores(
            amount, merchant, location, time, transaction_type
        )
        
        # Detect fraud
        is_fraud, message = fraud_engine.detect_fraud(risk_analysis)
        
        # Create transaction record
        transaction = Transaction(
            card_number=card_number,
            amount=amount,
            merchant=merchant,
            location=location,
            time=time,
            transaction_type=transaction_type,
            is_fraud=is_fraud,
            risk_score=risk_analysis['total_risk'],
            timestamp=datetime.datetime.now().strftime('%H:%M:%S')
        )
        
        # Add to history
        transactions_history.append(transaction)
        
        # Keep only last 50 transactions
        if len(transactions_history) > 50:
            transactions_history.pop(0)
        
        # Update statistics
        update_statistics(is_fraud)
        
        # Return analysis results
        return jsonify({
            'success': True,
            'is_fraud': is_fraud,
            'risk_analysis': risk_analysis,
            'message': message,
            'transaction': {
                'cardNumber': card_number,
                'amount': amount,
                'merchant': merchant,
                'location': location,
                'time': time,
                'type': transaction_type,
                'riskScore': risk_analysis['total_risk'],
                'timestamp': transaction.timestamp
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/api/get_transactions')
def get_transactions():
    """API endpoint to get recent transaction history"""
    
    # Return last 10 transactions
    recent_transactions = transactions_history[-10:] if transactions_history else []
    
    transactions_data = []
    for tx in recent_transactions:
        transactions_data.append({
            'cardNumber': tx.card_number,
            'amount': tx.amount,
            'merchant': tx.merchant,
            'location': tx.location,
            'time': tx.time,
            'type': tx.transaction_type,
            'isFraud': tx.is_fraud,
            'riskScore': tx.risk_score,
            'timestamp': tx.timestamp
        })
    
    return jsonify({
        'success': True,
        'transactions': transactions_data
    })

@app.route('/api/get_statistics')
def get_statistics():
    """API endpoint to get current statistics"""
    
    # Calculate detection rate
    if statistics['total'] > 0:
        statistics['detection_rate'] = round(
            (statistics['fraud'] / statistics['total']) * 100, 1
        )
    
    return jsonify({
        'success': True,
        'statistics': statistics
    })

@app.route('/api/generate_sample_transaction')
def generate_sample_transaction():
    """API endpoint to generate a sample transaction for demonstration"""
    
    merchants = ['amazon', 'walmart', 'target', 'bestbuy', 'unknown']
    locations = ['online', 'local', 'domestic', 'international']
    types = ['purchase', 'withdrawal', 'transfer', 'refund']
    
    # Generate random transaction
    sample_transaction = {
        'cardNumber': '**** **** **** ' + str(random.randint(1000, 9999)),
        'amount': round(random.uniform(10, 2000), 2),
        'merchant': random.choice(merchants),
        'location': random.choice(locations),
        'time': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
        'transactionType': random.choice(types)
    }
    
    # Analyze the sample transaction
    risk_analysis = fraud_engine.calculate_risk_scores(
        sample_transaction['amount'],
        sample_transaction['merchant'],
        sample_transaction['location'],
        sample_transaction['time'],
        sample_transaction['transactionType']
    )
    
    is_fraud, message = fraud_engine.detect_fraud(risk_analysis)
    
    # Create transaction record
    transaction = Transaction(
        card_number=sample_transaction['cardNumber'],
        amount=sample_transaction['amount'],
        merchant=sample_transaction['merchant'],
        location=sample_transaction['location'],
        time=sample_transaction['time'],
        transaction_type=sample_transaction['transactionType'],
        is_fraud=is_fraud,
        risk_score=risk_analysis['total_risk'],
        timestamp=datetime.datetime.now().strftime('%H:%M:%S')
    )
    
    # Add to history
    transactions_history.append(transaction)
    
    # Keep only last 50 transactions
    if len(transactions_history) > 50:
        transactions_history.pop(0)
    
    # Update statistics
    update_statistics(is_fraud)
    
    return jsonify({
        'success': True,
        'transaction': {
            'cardNumber': transaction.card_number,
            'amount': transaction.amount,
            'merchant': transaction.merchant,
            'location': transaction.location,
            'time': transaction.time,
            'type': transaction.transaction_type,
            'isFraud': is_fraud,
            'riskScore': risk_analysis['total_risk'],
            'timestamp': transaction.timestamp
        },
        'risk_analysis': risk_analysis,
        'message': message
    })

@app.route('/api/get_alerts')
def get_alerts():
    """API endpoint to get recent fraud alerts"""
    
    # Get recent fraud transactions (last 5)
    fraud_transactions = [tx for tx in transactions_history if tx.is_fraud][-5:]
    
    alerts = []
    for tx in fraud_transactions:
        alerts.append({
            'amount': tx.amount,
            'merchant': tx.merchant,
            'location': tx.location,
            'timestamp': tx.timestamp,
            'riskScore': tx.risk_score
        })
    
    return jsonify({
        'success': True,
        'alerts': alerts
    })

def update_statistics(is_fraud: bool):
    """Update global statistics"""
    statistics['total'] += 1
    if is_fraud:
        statistics['fraud'] += 1
    else:
        statistics['legitimate'] += 1
    
    # Calculate detection rate
    if statistics['total'] > 0:
        statistics['detection_rate'] = round(
            (statistics['fraud'] / statistics['total']) * 100, 1
        )

@app.route('/api/reset_statistics')
def reset_statistics():
    """API endpoint to reset all statistics and history"""
    
    global transactions_history, statistics
    
    transactions_history.clear()
    statistics = {
        'total': 0,
        'fraud': 0,
        'legitimate': 0,
        'detection_rate': 0.0
    }
    
    return jsonify({
        'success': True,
        'message': 'Statistics and history reset successfully'
    })

@app.route('/api/health')
def health_check():
    """API endpoint for health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("Starting Credit Card Fraud Detection Server...")
    print("Server will be available at: http://localhost:5000")
    print("API Documentation:")
    print("  GET  /api/health - Health check")
    print("  POST /api/analyze_transaction - Analyze transaction")
    print("  GET  /api/get_transactions - Get transaction history")
    print("  GET  /api/get_statistics - Get statistics")
    print("  GET  /api/generate_sample_transaction - Generate sample")
    print("  GET  /api/get_alerts - Get fraud alerts")
    print("  GET  /api/reset_statistics - Reset all data")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
