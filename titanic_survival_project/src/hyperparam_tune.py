import os
import joblib
from pprint import pprint

try:
    from .data_processing import load_data, prepare_X_y
    from .pipeline import build_preprocessor, get_models
except Exception:
    from titanic_survival_project.src.data_processing import load_data, prepare_X_y
    from titanic_survival_project.src.pipeline import build_preprocessor, get_models

from sklearn.model_selection import RandomizedSearchCV
import numpy as np


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def tune(n_iter=12, cv=3, random_state=42):
    df = load_data()
    X, y = prepare_X_y(df)

    numeric_features = ['Age', 'Fare', 'FamilySize', 'SharedTicketCount', 'NormalizedFare', 'FamilyCohesion']
    categorical_features = ['Pclass', 'Sex', 'Embarked', 'HonorificCode', 'IsAlone', 'CabinFlag']

    preprocessor = build_preprocessor(numeric_features, categorical_features, with_novel=True)
    models = get_models()

    results = {}
    rf_param = {
        'clf__n_estimators': [100, 200, 500],
        'clf__max_depth': [None, 5, 10, 20],
        'clf__min_samples_split': [2, 5, 10],
        'clf__max_features': ['sqrt', 'log2', None]
    }

    gb_param = {
        'clf__n_estimators': [100, 200, 300],
        'clf__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'clf__max_depth': [3, 5, 8],
        'clf__subsample': [0.6, 0.8, 1.0]
    }

    from sklearn.pipeline import Pipeline

    for name in ('random_forest', 'gradient_boosting'):
        print('\nTuning', name)
        base_clf = models[name]
        pipe = Pipeline([('pre', preprocessor), ('clf', base_clf)])
        param_dist = rf_param if name == 'random_forest' else gb_param

        rnd = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=n_iter, cv=cv,
                                 scoring='f1', n_jobs=-1, random_state=random_state, verbose=1)
        rnd.fit(X, y)
        print('Best params for', name)
        pprint(rnd.best_params_)
        print('Best CV score (f1):', rnd.best_score_)
        results[name] = {'best_estimator': rnd.best_estimator_, 'best_score': float(rnd.best_score_), 'best_params': rnd.best_params_}

        models_dir = os.path.join(_project_root(), 'models')
        os.makedirs(models_dir, exist_ok=True)
        save_path = os.path.join(models_dir, f'{name}_tuned_pipeline.joblib')
        joblib.dump(rnd.best_estimator_, save_path)
        print('Saved tuned pipeline to', save_path)

    return results


if __name__ == '__main__':
    res = tune(n_iter=12, cv=3)
    print('\nTuning complete. Summary:')
    for k, v in res.items():
        print(k, '->', v['best_score'])
