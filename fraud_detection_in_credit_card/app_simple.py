#!/usr/bin/env python3
"""
Simple Credit Card Fraud Detection Flask App
==========================================

A simple Flask application for credit card fraud detection prediction.
"""

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    """Serve the simple fraud detection page"""
    return render_template('index_simple.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'Simple Fraud Detection App is running'}

if __name__ == '__main__':
    print("🚀 Starting Simple Fraud Detection App...")
    print("📱 Open your browser to: http://localhost:5001")
    print("🛡️ Simple fraud prediction interface ready!")
    app.run(debug=True, host='0.0.0.0', port=5001)
