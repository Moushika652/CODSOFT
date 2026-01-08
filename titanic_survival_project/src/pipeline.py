from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import make_scorer, accuracy_score, f1_score, precision_score, recall_score
import numpy as np


class NovelFeatureAdder(BaseEstimator, TransformerMixin):
    def __init__(self, ticket_col='Ticket'):
        self.ticket_col = ticket_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        if 'FamilyCohesion' not in X.columns:
            if 'FamilySize' in X.columns and 'Age' in X.columns and self.ticket_col in X.columns:
                age_std = X.groupby(self.ticket_col)['Age'].transform('std').fillna(0)
                X['FamilyCohesion'] = X['FamilySize'] * np.exp(-0.1 * age_std)
            else:
                X['FamilyCohesion'] = X.get('FamilySize', 1)
        if 'NormalizedFare' not in X.columns and 'Fare' in X.columns and 'FamilySize' in X.columns:
            X['NormalizedFare'] = X['Fare'] / X['FamilySize']
            X['NormalizedFare'].replace([np.inf, -np.inf], np.nan, inplace=True)
        return X


def build_preprocessor(numeric_features, categorical_features, with_novel=True):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='Unknown')),
        ('ohe', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = None
    if with_novel:
        preprocessor = Pipeline(steps=[
            ('novel', NovelFeatureAdder()),
            ('cols', ColumnTransformer(transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]))
        ])
    else:
        preprocessor = ColumnTransformer(transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    return preprocessor


def get_models(random_state=42):
    models = {
        'logistic': LogisticRegression(max_iter=1000, random_state=random_state),
        'random_forest': RandomForestClassifier(n_estimators=200, random_state=random_state),
        'gradient_boosting': GradientBoostingClassifier(n_estimators=200, random_state=random_state)
    }
    return models


def evaluate_models(X, y, preprocessor, models, cv_splits=5):
    results = {}
    cv = StratifiedKFold(n_splits=cv_splits, shuffle=True, random_state=42)
    scoring = {
        'accuracy': make_scorer(accuracy_score),
        'f1': make_scorer(f1_score),
        'precision': make_scorer(precision_score),
        'recall': make_scorer(recall_score)
    }
    for name, clf in models.items():
        pipe = Pipeline(steps=[('pre', preprocessor), ('clf', clf)])
        cv_results = cross_validate(pipe, X, y, cv=cv, scoring=scoring, n_jobs=-1)
        results[name] = {k: float(cv_results['test_' + k].mean()) for k in scoring.keys()}
    return results
