import os
import math
import pandas as pd  # type: ignore
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, abort

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Simple credentials (for demo). Override with environment variables.
DEMO_USER = os.environ.get('DEMO_USER', 'admin')
DEMO_PASS = os.environ.get('DEMO_PASS', 'admin')

PREDICTIONS_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'predictions_all.csv'))
DEFAULT_THRESHOLD = float(os.environ.get('SURVIVAL_THRESHOLD', 0.7))


def load_predictions(path: str = None) -> pd.DataFrame:
    """Load predictions CSV safely. Returns empty DataFrame if file missing (so templates still render)."""
    csv_path = path or PREDICTIONS_CSV
    if not os.path.exists(csv_path):
        # return empty df with some expected columns to avoid template errors
        cols = ['PassengerId', 'Name', 'Predicted', 'PredictedProb', 'Survived', 'Sex', 'Age', 'Fare', 'Ticket', 'Cabin', 'Embarked']
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(csv_path)  # type: ignore
    df.columns = [c.strip() for c in df.columns]
    if 'PredictedProb' in df.columns:
        df['PredictedProb'] = pd.to_numeric(df['PredictedProb'], errors='coerce').fillna(0.0)
    return df


def is_safe_url(target: str) -> bool:
    """Ensure redirect targets are same host for safety."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https')) and (ref_url.netloc == test_url.netloc)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_user():
    return dict(
        current_user=session.get('username'),
        app_name='Titanic Predictions',
        page_title='Titanic Lifeboat Prediction',
        page_description='Predicts which passengers would survive using a lifeboat allocation model.',
        app_version=os.environ.get('APP_VERSION', '1.0'),
        app_author=os.environ.get('APP_AUTHOR', 'CODSOFT'),
        threshold_used=DEFAULT_THRESHOLD
    )


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next') or url_for('dashboard')
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if user == DEMO_USER and pw == DEMO_PASS:
            session['username'] = user
            if is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', next=next_url)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    df = load_predictions()
    threshold = DEFAULT_THRESHOLD

    # Determine groups
    if 'PredictedProb' in df.columns and df.shape[0] > 0:
        survived_mask = df['PredictedProb'].astype(float) >= threshold
    elif 'Predicted' in df.columns and df.shape[0] > 0:
        survived_mask = df['Predicted'].astype(str).str.lower().isin(['1', 'true', 'yes', 'survived'])
    elif 'Survived' in df.columns and df.shape[0] > 0:
        survived_mask = pd.to_numeric(df['Survived'], errors='coerce') == 1
    else:
        survived_mask = pd.Series([], dtype=bool)

    survived_count = int(survived_mask.sum()) if survived_mask.size else 0
    total_count = int(len(df))
    not_survived_count = total_count - survived_count
    survived_percent = round((survived_count / total_count * 100), 2) if total_count > 0 else 0.0
    not_survived_percent = round(100 - survived_percent, 2) if total_count > 0 else 0.0

    # inferred sex count placeholder (templates expect it)
    inferred_sex_count = int(df.get('_sex_inferred', pd.Series([], dtype=int)).sum()) if '_sex_inferred' in df.columns else 0

    return render_template(
        'dashboard.html',
        survived_count=survived_count,
        not_survived_count=not_survived_count,
        survived_percent=survived_percent,
        not_survived_percent=not_survived_percent,
        total_count=total_count,
        threshold_used=threshold,
        achieved_accuracy=None,
        inferred_sex_count=inferred_sex_count,
        message=None
    )


def _split_df(df: pd.DataFrame):
    """Return (survived_df, not_survived_df) using same logic as dashboard."""
    if 'PredictedProb' in df.columns:
        mask = df['PredictedProb'].astype(float) >= DEFAULT_THRESHOLD
    elif 'Predicted' in df.columns:
        mask = df['Predicted'].astype(str).str.lower().isin(['1', 'true', 'yes', 'survived'])
    elif 'Survived' in df.columns:
        mask = pd.to_numeric(df['Survived'], errors='coerce') == 1
    else:
        mask = pd.Series([False] * len(df))
    return df[mask].copy(), df[~mask].copy()


def find_threshold_for_target_accuracy(df: pd.DataFrame, target: float = 0.7, step: float = 0.01):
    """Attempt to find a PredictedProb threshold that yields approximate target proportion predicted survived.
    Returns (threshold, achieved_proportion) or (None, None) if not applicable.
    """
    if 'PredictedProb' not in df.columns or df.shape[0] == 0:
        return None, None
    total = len(df)
    best = None
    for t in [round(x * step, 3) for x in range(int(1/step)+1)]:
        prop = (df['PredictedProb'] >= t).sum() / total
        if prop >= target:
            return t, round(prop, 3)
        best = (t, round(prop, 3))
    return best


@app.route('/survived')
@login_required
def view_survived():
    df = load_predictions()
    s, _ = _split_df(df)
    html = s.to_html(classes='table table-striped', index=False) if not s.empty else "<p>No rows</p>"
    return render_template('list.html', title='Survived', table_html=html)


@app.route('/not_survived')
@login_required
def view_not_survived():
    df = load_predictions()
    _, ns = _split_df(df)
    html = ns.to_html(classes='table table-striped', index=False) if not ns.empty else "<p>No rows</p>"
    return render_template('list.html', title='Not survived', table_html=html)


@app.route('/download')
@login_required
def download():
    if not os.path.exists(PREDICTIONS_CSV):
        flash('CSV not found on server', 'warning')
        return redirect(url_for('dashboard'))
    return send_file(PREDICTIONS_CSV, as_attachment=True)


@app.route('/enrich', methods=['POST'])
@login_required
def enrich_dataset():
    # simple placeholder: report success if file exists
    if not os.path.exists(PREDICTIONS_CSV):
        flash('Cannot enrich — CSV not found', 'danger')
    else:
        flash('Enriched dataset saved (no-op in demo)', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
