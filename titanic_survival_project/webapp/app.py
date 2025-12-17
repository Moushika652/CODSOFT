import os
from functools import wraps
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import pandas as pd
import math

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Simple credentials (for demo). Override with environment variables.
DEMO_USER = os.environ.get('DEMO_USER', 'admin')
DEMO_PASS = os.environ.get('DEMO_PASS', 'admin')

PREDICTIONS_CSV = os.path.join(os.path.dirname(__file__), '..', 'predictions_all.csv')


def load_predictions():
    path = os.path.abspath(PREDICTIONS_CSV)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path) #type:ignore
    # normalize column names
    df.columns = [c.strip() for c in df.columns]

    # ensure PredictedProb numeric where present
    if 'PredictedProb' in df.columns:
        df['PredictedProb'] = pd.to_numeric(df['PredictedProb'], errors='coerce')

    # ensure Sex column exists; try to enrich from cleaned dataset or infer from Name
    df['_sex_inferred'] = False
    # If Sex is missing or empty, first try to join with a cleaned dataset that includes Name/Sex/Age
    cleaned_path = os.path.join(os.path.dirname(__file__), '..', 'titanic_cleaned_same_shape.csv')
    # normalize PassengerId in predictions (if present) to numeric for reliable joins
    if 'PassengerId' in df.columns:
        df['PassengerId'] = pd.to_numeric(df['PassengerId'], errors='coerce')
    if 'Sex' not in df.columns or df['Sex'].astype(str).str.strip().eq('').all():
        if os.path.exists(cleaned_path):
            try:
                meta = pd.read_csv(os.path.abspath(cleaned_path), usecols=['PassengerId', 'Name', 'Sex', 'Age'])
                # coerce PassengerId in meta as well
                if 'PassengerId' in meta.columns:
                    meta['PassengerId'] = pd.to_numeric(meta['PassengerId'], errors='coerce')
                # perform merge on numeric PassengerId
                df = df.merge(meta, on='PassengerId', how='left', suffixes=('', '_meta'))
                # prefer Sex from predictions if present; otherwise fill from meta
                if 'Sex_meta' in df.columns:
                    if 'Sex' not in df.columns:
                        df['Sex'] = ''
                    df['Sex'] = df['Sex'].astype(str).str.strip()
                    missing_mask = df['Sex'] == ''
                    df.loc[missing_mask, 'Sex'] = df.loc[missing_mask, 'Sex_meta'].astype(str).str.strip()
                    # mark those filled from meta as inferred
                    df.loc[missing_mask & df['Sex'].ne(''), '_sex_inferred'] = True
                    try:
                        df.drop(columns=['Sex_meta'], inplace=True)
                    except Exception:
                        pass
            except Exception:
                pass

    # if Sex still missing, try to infer from Name field
    if 'Sex' not in df.columns or df['Sex'].astype(str).str.strip().eq('').all():
        def infer_sex_from_name(name: str):
            if not isinstance(name, str):
                return ''
            lower = name.lower()
            if ' master.' in lower or ' master ' in lower or ', master' in lower:
                return 'male'
            if ' mr.' in lower or ' mr ' in lower or ', mr' in lower:
                return 'male'
            if ' mrs.' in lower or ' mrs ' in lower or ', mrs' in lower:
                return 'female'
            if ' miss.' in lower or ' miss ' in lower or ', miss' in lower:
                return 'female'
            if ' ms.' in lower or ' ms ' in lower or ', ms' in lower:
                return 'female'
            if ' mme.' in lower or ' mademoiselle' in lower:
                return 'female'
            if ' lady.' in lower or ' lady ' in lower:
                return 'female'
            return ''

        if 'Name' in df.columns:
            inferred = df['Name'].apply(infer_sex_from_name).astype(str).str.strip().str.lower()
            if 'Sex' not in df.columns:
                df['Sex'] = inferred
                df['_sex_inferred'] = inferred.str.len() > 0
            else:
                missing_mask = df['Sex'].astype(str).str.strip() == ''
                df.loc[missing_mask, 'Sex'] = inferred[missing_mask]
                df.loc[missing_mask & (inferred.str.len() > 0), '_sex_inferred'] = True

    # normalize Sex values to 'male'/'female' or empty
    # ensure a Sex column exists so subsequent operations don't KeyError
    if 'Sex' not in df.columns:
        df['Sex'] = ''
    def _normalize_sex_value(v):
        if not isinstance(v, str):
            return ''
        s = v.strip().lower()
        if not s:
            return ''
        # common normalized values
        if s in ('male', 'm', 'mr', 'master', 'sir'):
            return 'male'
        if s in ('female', 'f', 'mrs', 'miss', 'ms', 'mme', 'lady'):
            return 'female'
        # fallback: single-letter codes
        if s == 'm':
            return 'male'
        if s == 'f':
            return 'female'
        return ''

    df['Sex'] = df['Sex'].apply(_normalize_sex_value)
    # if Sex was present originally, ensure _sex_inferred is False for those rows
    if '_sex_inferred' in df.columns:
        present_mask = df['Sex'].isin(['male', 'female'])
        # ensure inferred flag only true for rows we actually inferred
        df.loc[~present_mask, '_sex_inferred'] = False

    return df


def is_safe_url(target: str) -> bool:
    try:
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return (test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc)
    except Exception:
        return False


def login_required(f):
    # Authentication removed per UI requirement — make decorator a no-op
    return f


@app.context_processor
def inject_user():
    return dict(current_user=session.get('username'), app_name='Titanic Predictions')


@app.route('/')
def index():
    # Redirect root to dashboard so app opens directly to survived/not-survived view
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Login page removed: redirect to home
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
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
    threshold_used = None
    achieved_accuracy = None
    if 'PredictedProb' in df.columns:
        try:
            # if we have ground-truth labels, try to select a threshold that reaches TARGET_ACCURACY (default 0.7)
            if 'Survived' in df.columns:
                target = float(os.environ.get('TARGET_ACCURACY', 0.7))
                threshold_used, achieved_accuracy = find_threshold_for_target_accuracy(df, target=target)
            else:
                threshold_used = float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9))
        except Exception:
            threshold_used = 0.7
        df_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') >= threshold_used] #type:ignore
        df_not_survived = df[pd.to_numeric(df['PredictedProb'], errors='coerce') < threshold_used] #type:ignore
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

    # compute groups: male, female, child (child determined by age threshold)
    def _col_name(df: pd.DataFrame, target: str):
        for c in df.columns:
            if str(c).lower() == target.lower():
                return c
        return None

    sex_col = _col_name(df, 'sex')
    age_col = _col_name(df, 'age')
    try:
        child_age = int(os.environ.get('CHILD_AGE', 18))
    except Exception:
        child_age = 18

    def _counts_by_group(df_group: pd.DataFrame):
        counts = {'male': 0, 'female': 0, 'child': 0}
        if df_group.empty:
            return counts
        # count male/female when sex column exists
        if sex_col is not None:
            s = df_group[sex_col].astype(str).str.lower()
            counts['male'] = int((s == 'male').sum())
            counts['female'] = int((s == 'female').sum())
        # count children when age column exists
        if age_col is not None:
            a = pd.to_numeric(df_group[age_col], errors='coerce')
            counts['child'] = int((a < child_age).sum())
        return counts

    survived_by_group = _counts_by_group(df_survived)
    not_survived_by_group = _counts_by_group(df_not_survived)

    # expose primitive counts to templates to avoid Jinja attribute resolution issues
    survived_male = int(survived_by_group.get('male', 0))
    survived_female = int(survived_by_group.get('female', 0))
    survived_child = int(survived_by_group.get('child', 0))
    not_survived_male = int(not_survived_by_group.get('male', 0))
    not_survived_female = int(not_survived_by_group.get('female', 0))
    not_survived_child = int(not_survived_by_group.get('child', 0))

    # compute inferred sex count and pass an integer to templates (avoid passing DataFrame)
    inferred_sex_count = int(df['_sex_inferred'].sum()) if ('_sex_inferred' in df.columns) else 0
    return render_template(
        'dashboard.html',
        rows_survived=rows_survived,
        rows_not_survived=rows_not_survived,
        survived_count=survived_count,
        not_survived_count=not_survived_count,
        total_count=total_count,
        survived_percent=survived_percent,
        not_survived_percent=not_survived_percent,
        survived_by_sex=survived_by_group,
        not_survived_by_sex=not_survived_by_group,
        survived_male=survived_male,
        survived_female=survived_female,
        survived_child=survived_child,
        not_survived_male=not_survived_male,
        not_survived_female=not_survived_female,
        not_survived_child=not_survived_child,
        sex_col=sex_col,
        age_col=age_col,
        threshold_used=threshold_used,
        achieved_accuracy=achieved_accuracy,
        inferred_sex_count=inferred_sex_count,
        message=None,
    )


def _split_df(df: pd.DataFrame):
    # replicate the splitting logic used in dashboard
    if 'PredictedProb' in df.columns:
        try:
            # if a target accuracy is provided, try to find a threshold that yields approximately that accuracy
            if 'Survived' in df.columns and os.environ.get('TARGET_ACCURACY') is not None:
                target = float(os.environ.get('TARGET_ACCURACY', 0.7))
                threshold, _ = find_threshold_for_target_accuracy(df, target=target)
            else:
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


def find_threshold_for_target_accuracy(df: pd.DataFrame, target: float = 0.7, step: float = 0.01):
    """Search thresholds from 0.0..1.0 (step) and return the threshold that yields accuracy
    closest to `target` when ground-truth `Survived` is available. Returns (threshold, accuracy).
    """
    if 'PredictedProb' not in df.columns or 'Survived' not in df.columns:
        try:
            return float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9)), None
        except Exception:
            return 0.9, None

    probs = pd.to_numeric(df['PredictedProb'], errors='coerce')
    truth = pd.to_numeric(df['Survived'], errors='coerce')
    mask = probs.notnull() & truth.notnull()
    if mask.sum() == 0:
        return float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9)), None

    probs = probs[mask]
    truth = truth[mask].astype(int)

    best_t = None
    best_diff = float('inf')
    best_acc = None
    t = 0.0
    while t <= 1.0 + 1e-9:
        preds = (probs >= t).astype(int)
        acc = float((preds.values == truth.values).mean())
        diff = abs(acc - target)
        if diff < best_diff:
            best_diff = diff
            best_t = round(t, 4)
            best_acc = acc
        t += step

    return best_t, round(best_acc, 4) if best_acc is not None else (float(os.environ.get('SURVIVAL_PROB_THRESHOLD', 0.9)), None)


@app.route('/survived')
@login_required
def survived_page():
    df = load_predictions()
    if df.empty:
        return render_template('subset.html', rows=[], title='Survived', message='No predictions file found')
    df_survived, _ = _split_df(df)
    sel = request.args.get('sex')
    if sel:
        sel_l = sel.lower()
        if sel_l in ('male', 'female') and 'Sex' in df_survived.columns:
            df_survived = df_survived[df_survived['Sex'].astype(str).str.lower() == sel_l]
        elif sel_l == 'child' and 'Age' in df_survived.columns:
            try:
                ca = int(os.environ.get('CHILD_AGE', 18))
            except Exception:
                ca = 18
            df_survived = df_survived[pd.to_numeric(df_survived['Age'], errors='coerce') < ca]
    rows = df_survived.to_dict(orient='records') # type: ignore
    # remove Description field (not shown on subset pages)
    for r in rows:
        r.pop('Description', None)
    return render_template('subset.html', rows=rows, title='Survived', message=None)


@app.route('/not_survived')
@login_required
def not_survived_page():
    df = load_predictions()
    if df.empty:
        return render_template('subset.html', rows=[], title='Not survived', message='No predictions file found')
    _, df_not_survived = _split_df(df)
    sel = request.args.get('sex')
    if sel:
        sel_l = sel.lower()
        if sel_l in ('male', 'female') and 'Sex' in df_not_survived.columns:
            df_not_survived = df_not_survived[df_not_survived['Sex'].astype(str).str.lower() == sel_l]
        elif sel_l == 'child' and 'Age' in df_not_survived.columns:
            try:
                ca = int(os.environ.get('CHILD_AGE', 18))
            except Exception:
                ca = 18
            df_not_survived = df_not_survived[pd.to_numeric(df_not_survived['Age'], errors='coerce') < ca]
    rows = df_not_survived.to_dict(orient='records') # type: ignore
    for r in rows:
        r.pop('Description', None)
    return render_template('subset.html', rows=rows, title='Not survived', message=None)


@app.route('/download')
@login_required
def download():
    path = os.path.abspath(PREDICTIONS_CSV)
    if not os.path.exists(path):
        return 'Predictions file not found', 404
    return send_file(path, as_attachment=True)


@app.route('/enrich', methods=['POST'])
@login_required
def enrich_dataset():
    """Save an enriched copy of the predictions CSV including normalized `Sex` and
    `_sex_inferred` flags. Returns user to dashboard with a flash message."""
    df = load_predictions()
    if df.empty:
        flash('No predictions file found to enrich', 'danger')
        return redirect(url_for('dashboard'))
    out_path = os.path.join(os.path.dirname(os.path.abspath(PREDICTIONS_CSV)), 'predictions_with_sex.csv')
    # ensure we don't include internal-only columns if present
    to_save = df.copy()
    try:
        to_save.to_csv(out_path, index=False)
        flash(f'Enriched dataset saved to {out_path}', 'success')
    except Exception as e:
        flash(f'Failed to save enriched dataset: {e}', 'danger')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
