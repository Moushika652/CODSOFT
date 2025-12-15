
import os
import re
import numpy as np
import pandas as pd


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data(path: str = None) -> pd.DataFrame:
    """Load Titanic dataset (cleaned but same shape)."""
    if path is None:
        path = os.path.join(_project_root(), 'titanic_cleaned_same_shape.csv')
    """Load dataset. If `path` is None, search for `titanic_cleaned_same_shape.csv` in
    sensible locations (cwd and parent folders) and return the loaded DataFrame.
    """
    filename = 'titanic_cleaned_same_shape.csv'

    def _search_candidates():
        # 1. explicit cwd
        yield os.path.join(os.getcwd(), filename)
        # 2. relative to this file (src/ -> repo root)
        yield os.path.join(_project_root(), filename)
        # 3. walk upward from cwd
        cur = os.path.abspath(os.getcwd())
        while True:
            yield os.path.join(cur, filename)
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent

    if path is None:
        found = None
        for candidate in _search_candidates():
            if os.path.exists(candidate):
                found = candidate
                break
        if found is None:
            raise FileNotFoundError(
                f"Could not find '{filename}'. Please place it at the repository root or pass its path to load_data(path=...)."
            )
        path = found

    return pd.read_csv(path)


def parse_honorific(name: str) -> str:
    """Extract honorific from passenger name and normalize rare titles."""
    if pd.isna(name):
        return 'Unknown'

    match = re.search(r",\s*([A-Za-z]+)\.?", name)
    if match:
        title = match.group(1)
        mapping = {
            'Mlle': 'Miss',
            'Ms': 'Miss',
            'Mme': 'Mrs'
        }
        return mapping.get(title, title)

    return 'Other'


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Honorific extraction
    df['HonorificCode'] = df['Name'].apply(parse_honorific)

    # Family-based features
    df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

    # Ticket-based age variability (cohesion signal)
    age_std_by_ticket = df.groupby('Ticket')['Age'].transform('std').fillna(0)
    df['FamilyCohesion'] = df['FamilySize'] * np.exp(-0.1 * age_std_by_ticket)

    # Cabin availability flag
    df['CabinFlag'] = df['Cabin'].notna().astype(int)

    # Shared ticket count
    df['SharedTicketCount'] = df.groupby('Ticket')['Ticket'].transform('count')

    # Normalized fare
    df['NormalizedFare'] = df['Fare'] / df['FamilySize']
    df['NormalizedFare'] = df['NormalizedFare'].replace([np.inf, -np.inf], np.nan)
    df['NormalizedFare'] = df['NormalizedFare'].fillna(df['NormalizedFare'].median())

    # Reduce honorifics to stable categories
    common_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Dr']
    df['HonorificCode'] = df['HonorificCode'].apply(
        lambda t: t if t in common_titles else 'Other'
    )

    return df


def prepare_X_y(df: pd.DataFrame):
    df = engineer_features(df)

    if 'Survived' not in df.columns:
        raise KeyError("Target column 'Survived' not found")

    y = df['Survived'].astype(int)

    X = df[
        [
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
    ].copy()

    # Final safety fills
    X['Embarked'] = X['Embarked'].fillna('Unknown')
    X['Fare'] = X['Fare'].fillna(X['Fare'].median())

    return X, y


if __name__ == '__main__':
    df = load_data()
    X, y = prepare_X_y(df)
    print(f"Dataset loaded successfully: {len(X)} rows")
    print("Feature columns:")
    print(list(X.columns))
