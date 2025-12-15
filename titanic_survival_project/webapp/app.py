import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd

app = Flask(__name__, template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Simple credentials (for demo). Override with environment variables.
DEMO_USER = os.environ.get('DEMO_USER', 'admin')
DEMO_PASS = os.environ.get('DEMO_PASS', 'admin')

PREDICTIONS_CSV = os.path.join(os.path.dirname(__file__), '..', 'predictions_all.csv')


def load_predictions():
    path = os.path.abspath(PREDICTIONS_CSV)
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == DEMO_USER and password == DEMO_PASS:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    df = load_predictions()
    if df.empty:
        return render_template('dashboard.html', rows=[], message='No predictions file found')
    # show first 200 rows to keep page small
    rows = df.head(200).to_dict(orient='records')
    return render_template('dashboard.html', rows=rows, message=None)


@app.route('/download')
def download():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    path = os.path.abspath(PREDICTIONS_CSV)
    if not os.path.exists(path):
        return 'Predictions file not found', 404
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
