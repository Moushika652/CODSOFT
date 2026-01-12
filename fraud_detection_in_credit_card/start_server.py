#!/usr/bin/env python3
"""
Credit Card Fraud Detection Server Startup Script
================================================

Easy startup script for the fraud detection web application.
This script handles dependency installation and server startup.

Usage:
    python start_server.py
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("   Please run: pip install -r requirements.txt")
        sys.exit(1)

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        "server.py",
        "templates/index.html",
        "static/script.js",
        "static/styles.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    print("✅ All required files found!")

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting Credit Card Fraud Detection Server...")
    print("=" * 60)
    print("Server will be available at: http://localhost:5000")
    print("API Documentation:")
    print("  GET  /api/health - Health check")
    print("  POST /api/analyze_transaction - Analyze transaction")
    print("  GET  /api/get_transactions - Get transaction history")
    print("  GET  /api/get_statistics - Get statistics")
    print("  GET  /api/generate_sample_transaction - Generate sample")
    print("  GET  /api/get_alerts - Get fraud alerts")
    print("  GET  /api/reset_statistics - Reset all data")
    print("=" * 60)
    print("\n📝 Press Ctrl+C to stop the server")
    print("🌐 Opening browser in 3 seconds...")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open('http://localhost:5000')
            print("✅ Browser opened!")
        except:
            print("⚠️  Could not open browser automatically")
            print("   Please manually open: http://localhost:5000")
    
    # Start browser opening in background
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the Flask server
    try:
        from server import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🔍 Credit Card Fraud Detection Server Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check file structure
    check_file_structure()
    
    # Ask user if they want to install dependencies
    if len(sys.argv) > 1 and sys.argv[1] == "--no-install":
        print("⏭️  Skipping dependency installation")
    else:
        install_dependencies()
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()
