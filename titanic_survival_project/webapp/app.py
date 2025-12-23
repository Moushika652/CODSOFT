import os
from typing import Optional, Tuple

from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, abort

import pandas as pd

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

DEMO_USER: str = os.environ.get('DEMO_USER', 'admin')
DEMO_PASS: str = os.environ.get('DEMO_PASS', 'admin')

PREDICTIONS_CSV: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'predictions_all.csv'))
DEFAULT_THRESHOLD = float(os.environ.get('SURVIVAL_THRESHOLD', 0.7))


def load_predictions(path: Optional[str] = None) -> pd.DataFrame:
    csv_path = path or PREDICTIONS_CSV
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path) # type: ignore
    df.columns = [c.strip() for c in df.columns]
    if 'PredictedProb' in df.columns:
        df['PredictedProb'] = pd.to_numeric(df['PredictedProb'], errors='coerce').fillna(0.0) # type: ignore
    return df


def is_safe_url(target: str) -> bool:
    base = str(request.host_url)
    ref_url = urlparse(base)
    test_url = urlparse(urljoin(base, target))
    return (test_url.scheme in ('http', 'https')) and (ref_url.netloc == test_url.netloc)


def login_required(f):
    @wraps(f) # type: ignore
    def decorated(*args, **kwargs):
        # no-op: allow access without login
        return f(*args, **kwargs)
    return decorated


@app.context_processor
def inject_user() -> dict:
    return {"app_name": "Titanic Survival", "user": DEMO_USER}


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
    total = len(df) if df is not None else 0

    survived_df, not_survived_df = _split_df(df)
    surv_count = len(survived_df)
    not_count = len(not_survived_df)

    surv_pct = round((surv_count / total * 100) if total > 0 else 0.0, 2)
    not_pct = round((not_count / total * 100) if total > 0 else 0.0, 2)

    return render_template(
        'dashboard.html',
        # counts / totals
        total=total,
        total_count=total,
        survived_count=surv_count,
        not_survived_count=not_count,
        # percentages (provide both variable names used in template)
        survived_pct=surv_pct,
        not_survived_pct=not_pct,
        survived_percent=surv_pct,
        not_survived_percent=not_pct,
        # optional extras your template references
        threshold_used=DEFAULT_THRESHOLD,
        page_title="Titanic Lifeboat Prediction"
    )


def _split_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # prefer predicted probability column if present
    if 'PredictedProb' in df.columns:
        try:
            probs = pd.to_numeric(df['PredictedProb'], errors='coerce') # type: ignore
            survived_mask = probs >= DEFAULT_THRESHOLD
            return df[survived_mask].copy(), df[~survived_mask].copy()
        except Exception:
            pass

    # fallback to Survived column if present
    if 'Survived' in df.columns:
        try:
            surv = pd.to_numeric(df['Survived'], errors='coerce').fillna(0).astype(int) # type: ignore
            return df[surv == 1].copy(), df[surv == 0].copy()
        except Exception:
            pass

    # otherwise nothing classified
    return pd.DataFrame(), df.copy()


@app.route('/survived')
@login_required
def view_survived():
    df = load_predictions()
    s, _ = _split_df(df)
    table_html = s.to_html(classes='table table-striped', index=False) if not s.empty else "<p>No rows to show.</p>"
    return render_template('list.html', title='Survived', table_html=table_html, page_class='survived')


@app.route('/not_survived')
@login_required
def view_not_survived():
    df = load_predictions()
    _, ns = _split_df(df)
    table_html = ns.to_html(classes='table table-striped', index=False) if not ns.empty else "<p>No rows to show.</p>"
    return render_template('list.html', title='Not survived', table_html=table_html, page_class='not-survived')


@app.route('/download')
@login_required
def download():
    if not os.path.exists(PREDICTIONS_CSV):
        flash("No predictions file available.", "warning")
        return redirect(url_for('dashboard'))
    return send_file(PREDICTIONS_CSV, as_attachment=True, download_name=os.path.basename(PREDICTIONS_CSV))


@app.route('/enrich', methods=['POST'])
@login_required
def enrich():
    # lightweight placeholder: accept form and re-save CSV if present
    df = load_predictions()
    if df.empty:
        flash("No data to enrich.", "warning")
        return redirect(url_for('dashboard'))
    # Example: add a column if requested
    col = request.form.get('col_name')
    if col:
        df[col] = request.form.get('col_value', '')
        df.to_csv(PREDICTIONS_CSV, index=False)
        flash(f"Added column {col}.", "success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)
