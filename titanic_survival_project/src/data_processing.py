import os
import re
from typing import Optional, Tuple

import pandas as pd
import numpy as np


def _project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data(path: Optional[str] = None) -> pd.DataFrame:
    """Load Titanic dataset (cleaned). Search repo root if path not provided."""
    filename = 'titanic_cleaned_same_shape.csv'
    if path is None:
        # candidate search: cwd, project root, upward walk
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

    return pd.read_csv(path) # type: ignore


def parse_honorific(name: str) -> str:
    """Extract honorific from passenger name and normalize rare titles."""
    if pd.isna(name): # type: ignore
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

    # Honorific extraction
    df['HonorificCode'] = df['Name'].apply(parse_honorific) # type: ignore

    # Family-based features
    df['FamilySize'] = df.get('SibSp', 0).fillna(0).astype(int) + df.get('Parch', 0).fillna(0).astype(int) + 1 # type: ignore
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

    # Ticket-based age variability (cohesion signal)
    age_std_by_ticket: pd.Series = df.groupby('Ticket')['Age'].transform('std').fillna(0) # type: ignore
    df['FamilyCohesion'] = df['FamilySize'] * np.exp(-0.1 * age_std_by_ticket)

    # Cabin availability flag
    df['CabinFlag'] = df['Cabin'].notna().astype(int)

    # Shared ticket count
    df['SharedTicketCount'] = df.groupby('Ticket')['Ticket'].transform('count') # type: ignore

    # Normalized fare
    df['NormalizedFare'] = df.get('Fare', pd.Series(0)).astype(float) / df['FamilySize']
    df['NormalizedFare'].replace([np.inf, -np.inf], np.nan, inplace=True) # type: ignore
    if df['NormalizedFare'].isna().all():
        df['NormalizedFare'] = 0.0
    else:
        df['NormalizedFare'].fillna(df['NormalizedFare'].median(), inplace=True) # type: ignore

    # Reduce honorifics to stable categories
    common_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Dr']
    df['HonorificCode'] = df['HonorificCode'].apply(lambda t: t if t in common_titles else 'Other') # type: ignore

    return df


def prepare_X_y(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Return feature matrix X and target y (Survived)."""
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

    # Final safety fills
    if 'Embarked' in X.columns:
        X['Embarked'] = X['Embarked'].fillna('Unknown') # type: ignore
    if 'Fare' in X.columns:
        X['Fare'] = X['Fare'].fillna(X['Fare'].median()) # type: ignore

    return X, y


if __name__ == '__main__':
    df: pd.DataFrame = load_data()
    X, y = prepare_X_y(df)
    print(f"Dataset loaded successfully: {len(X)} rows")
    print("Feature columns:")
    print(list(X.columns))
