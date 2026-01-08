import os
import re
from typing import Optional, Tuple

import pandas as pd
import numpy as np


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data(path: Optional[str] = None) -> pd.DataFrame:
    filename = 'titanic_cleaned_same_shape.csv'
    if path is None:
        def _search_candidates():
            yield os.path.join(os.getcwd(), filename)
            yield os.path.join(_project_root(), filename)
            cur = os.path.abspath(os.getcwd())
            while True:
                yield os.path.join(cur, filename)
                parent = os.path.dirname(cur)
                if parent == cur:
                    break
                cur = parent

        found = None
        for candidate in _search_candidates():
            if os.path.exists(candidate):
                found = candidate
                break
        if found is None:
            raise FileNotFoundError(
                f"Could not find '{filename}'. Place it at the repository root or call load_data(path=...)."
            )
        path = found

    return pd.read_csv(path)


def parse_honorific(name: str) -> str:
    if pd.isna(name):
        return 'Unknown'
    s = str(name)
    match = re.search(r",\s*([A-Za-z]+)\.?", s)
    if match:
        title = match.group(1)
        mapping = {'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs'}
        return mapping.get(title, title)

    return 'Other'


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df['HonorificCode'] = df['Name'].apply(parse_honorific)

    df['FamilySize'] = df.get('SibSp', 0).fillna(0).astype(int) + df.get('Parch', 0).fillna(0).astype(int) + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

    age_std_by_ticket: pd.Series = df.groupby('Ticket')['Age'].transform('std').fillna(0)
    df['FamilyCohesion'] = df['FamilySize'] * np.exp(-0.1 * age_std_by_ticket)

    df['CabinFlag'] = df['Cabin'].notna().astype(int)

    df['SharedTicketCount'] = df.groupby('Ticket')['Ticket'].transform('count')

    df['NormalizedFare'] = df.get('Fare', pd.Series(0)).astype(float) / df['FamilySize']
    df['NormalizedFare'].replace([np.inf, -np.inf], np.nan, inplace=True)
    if df['NormalizedFare'].isna().all():
        df['NormalizedFare'] = 0.0
    else:
        df['NormalizedFare'].fillna(df['NormalizedFare'].median(), inplace=True)

    common_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Dr']
    df['HonorificCode'] = df['HonorificCode'].apply(lambda t: t if t in common_titles else 'Other')

    return df


def prepare_X_y(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    df = engineer_features(df)

    if 'Survived' not in df.columns:
        raise KeyError("Target column 'Survived' not found")

    y: pd.Series = df['Survived'].astype(int)

    cols = [
        'Pclass',
        'Sex',
        'Age',
        'Fare',
        'Embarked',
        'HonorificCode',
        'FamilySize',
        'FamilyCohesion',
        'IsAlone',
        'CabinFlag',
        'SharedTicketCount',
        'NormalizedFare'
    ]
    X = df[[c for c in cols if c in df.columns]].copy()

    if 'Embarked' in X.columns:
        X['Embarked'] = X['Embarked'].fillna('Unknown')
    if 'Fare' in X.columns:
        X['Fare'] = X['Fare'].fillna(X['Fare'].median())

    return X, y


if __name__ == '__main__':
    df: pd.DataFrame = load_data()
    X, y = prepare_X_y(df)
    print(f"Dataset loaded successfully: {len(X)} rows")
    print("Feature columns:")
    print(list(X.columns))
