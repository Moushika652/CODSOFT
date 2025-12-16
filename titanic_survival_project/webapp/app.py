import os
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import math

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
    return pd.read_csv(path) #type:ignore


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
    rows = [] #type:ignore
    df = load_predictions()
    if df.empty:
        return render_template(
            'dashboard.html',
            rows_survived=[],
            rows_not_survived=[],
            survived_count=0,
            not_survived_count=0,
            total_count=0,
            survived_percent=0.0,
            not_survived_percent=0.0,
            message='No predictions file found',
        )
    def describe_record(d: dict) -> str: # type: ignore
        parts = []
        # prefer Name or PassengerId
        if d.get('Name'): # type: ignore
            parts.append(f"Name: {d.get('Name')}") # type: ignore
        elif d.get('PassengerId'): # type: ignore
            parts.append(f"PassengerId: {d.get('PassengerId')}") # type: ignore
        # basic demographics
        if d.get('Sex'): # type: ignore
            parts.append(f"Sex: {d.get('Sex')}") # type: ignore
        if d.get('Age') and not (isinstance(d.get('Age'), float) and math.isnan(d.get('Age'))): # type: ignore
            parts.append(f"Age: {d.get('Age')}") # type: ignore
        if d.get('Pclass'): # type: ignore
            parts.append(f"Pclass: {d.get('Pclass')}") # type: ignore
        if d.get('Fare'): # type: ignore
            parts.append(f"Fare: {d.get('Fare')}") # type: ignore
        if d.get('Cabin'): # type: ignore
            parts.append(f"Cabin: {d.get('Cabin')}") # type: ignore
        if d.get('Embarked'): # type: ignore
            parts.append(f"Embarked: {d.get('Embarked')}") # type: ignore
        # prediction info
        prob = d.get('PredictedProb') or d.get('Probability') # type: ignore
        pred_label = None
        if 'Predicted' in d:
            pred_label = ('Survived' if d.get('Predicted') == 1 else 'Not survived') # type: ignore
        elif 'Survived' in d:
            pred_label = ('Survived' if d.get('Survived') == 1 else 'Not survived') # type: ignore
        if pred_label:
            parts.append(f"Model: {pred_label}") # type: ignore
        if prob is not None and not (isinstance(prob, float) and math.isnan(prob)):
            try:
                p = float(prob) # type: ignore
                parts.append(f"Prob: {p:.2f}") # type: ignore
            except Exception:
                parts.append(f"Prob: {prob}") # type: ignore
        return ' | '.join(parts) # type: ignore

    # show all rows (useful when full dataset needed)
    # Determine survival groups.
    # Prefer a probability column `PredictedProb` (use threshold, default 0.9),
    # then fall back to `Predicted` label or `Survived` column if present.
    if 'PredictedProb' in df.columns:
        try:
            threshold = float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9))
        except Exception:
            threshold = 0.9
        df_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') >= threshold] #type:ignore
        df_not_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') < threshold] #type:ignore
    elif 'Predicted' in df.columns:
        df_survived = df[df['Predicted'] == 1]
        df_not_survived = df[df['Predicted'] == 0]
    elif 'Survived' in df.columns:
        df_survived = df[df['Survived'] == 1]
        df_not_survived = df[df['Survived'] == 0]
    else:
        # fallback: no prediction column, treat all as not survived
        df_survived = df.iloc[0:0]
        df_not_survived = df

    rows_survived = df_survived.to_dict(orient='records')#type:ignore
    rows_not_survived = df_not_survived.to_dict(orient='records') # type: ignore

    # add human-friendly description for each record
    for rec in rows_survived:
        rec['Description'] = describe_record(rec)
    for rec in rows_not_survived:
        rec['Description'] = describe_record(rec)

    survived_count = len(rows_survived)
    not_survived_count = len(rows_not_survived)
    total_count = survived_count + not_survived_count
    survived_percent = round((survived_count / total_count * 100), 2) if total_count else 0.0
    not_survived_percent = round((not_survived_count / total_count * 100), 2) if total_count else 0.0

    return render_template(
        'dashboard.html',
        rows_survived=rows_survived,
        rows_not_survived=rows_not_survived,
        survived_count=survived_count,
        not_survived_count=not_survived_count,
        total_count=total_count,
        survived_percent=survived_percent,
        not_survived_percent=not_survived_percent,
        message=None,
    )


def _split_df(df: pd.DataFrame):
    # replicate the splitting logic used in dashboard
    if 'PredictedProb' in df.columns:
        try:
            threshold = float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9))
        except Exception:
            threshold = 0.9
        df_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') >= threshold] # type: ignore
        df_not_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') < threshold] # type: ignore
    elif 'Predicted' in df.columns:
        df_survived = df[df['Predicted'] == 1]
        df_not_survived = df[df['Predicted'] == 0]
    elif 'Survived' in df.columns:
        df_survived = df[df['Survived'] == 1]
        df_not_survived = df[df['Survived'] == 0]
    else:
        df_survived = df.iloc[0:0]
        df_not_survived = df
    return df_survived, df_not_survived


@app.route('/survived')
def survived_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    df = load_predictions()
    if df.empty:
        return render_template('subset.html', rows=[], title='Survived', message='No predictions file found')
    df_survived, _ = _split_df(df)
    rows = df_survived.to_dict(orient='records') # type: ignore
    # remove Description field (not shown on subset pages)
    for r in rows:
        r.pop('Description', None)
    return render_template('subset.html', rows=rows, title='Survived', message=None)


@app.route('/not_survived')
def not_survived_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    df = load_predictions()
    if df.empty:
        return render_template('subset.html', rows=[], title='Not survived', message='No predictions file found')
    _, df_not_survived = _split_df(df)
    rows = df_not_survived.to_dict(orient='records') # type: ignore
    for r in rows:
        r.pop('Description', None)
    return render_template('subset.html', rows=rows, title='Not survived', message=None)


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
