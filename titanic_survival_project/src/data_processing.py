import os
import re
import numpy as np
import pandas as pd


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data(path: str = None) -> pd.DataFrame:
    """Load dataset. By default loads the workspace CSV file in the repo root."""
    if path is None:
        path = os.path.join(_project_root(), 'titanic_cleaned_same_shape.csv')
    return pd.read_csv(path)


def parse_honorific(name: str) -> str:
    """Extract an honorific with a tolerant regex and normalized mapping.

    This function uses a permissive regex, then maps uncommon forms to 'Other'.
    """
    if pd.isna(name):
        return 'Unknown'
    m = re.search(r",\s*([^\.\,]+)\.?\s*", name)
    if m:
        t = m.group(1).strip()
        # normalize some common variants
        mapping = {
            'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs', 'Lady': 'Lady', 'Countess': 'Other'
        }
        return mapping.get(t, t)
    # final fallback
    return 'Other'


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Honorifics
    df['HonorificCode'] = df['Name'].apply(parse_honorific)

    # Family features: family size and a novel "family cohesion" score
    df['FamilySize'] = df.get('SibSp', 0) + df.get('Parch', 0) + 1
    # cohort age variability per shared ticket — smaller variance suggests closer family grouping
    age_std_by_ticket = df.groupby('Ticket')['Age'].transform('std').fillna(0)
    # FamilyCohesion: larger family and low within-ticket age std increases cohesion
    df['FamilyCohesion'] = df['FamilySize'] * np.exp(-0.1 * age_std_by_ticket)

    # Single-traveler flag
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

    # Cabin presence flag (named nontrivially)
    df['CabinFlag'] = (~df.get('Cabin', pd.Series([np.nan]*len(df))).isna()).astype(int)

    # Shared ticket count
    df['SharedTicketCount'] = df.groupby('Ticket')['Ticket'].transform('count')

    # Normalized fare per apparent family
    df['NormalizedFare'] = df['Fare'] / df['FamilySize']
    df['NormalizedFare'] = df['NormalizedFare'].replace([np.inf, -np.inf], np.nan)

    # Impute Age sensibly: median per Title, fallback to global median
    age_medians = df.groupby('HonorificCode')['Age'].median()
    global_median = df['Age'].median()

    def impute_age(row):
        if pd.isna(row['Age']):
            t = row['HonorificCode']
            if not pd.isna(age_medians.get(t, np.nan)):
                return age_medians[t]
            return global_median
        return row['Age']

    df['Age'] = df.apply(impute_age, axis=1)

    # Reduce Honorific codes to a short set
    common_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Dr']
    df['HonorificCode'] = df['HonorificCode'].apply(lambda t: t if t in common_titles else 'Other')

    # Final tidy: select useful columns (keep original columns too)
    # leave downstream code to pick features; return enriched dataframe
    return df


def prepare_X_y(df: pd.DataFrame):
    df = engineer_features(df)
    # Label
    if 'Survived' not in df.columns:
        raise KeyError('Dataset must contain Survived column')
    y = df['Survived'].astype(int)

    # Candidate features (engineered names intentionally distinct)
    X = df[['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'HonorificCode', 'FamilySize', 'FamilyCohesion', 'IsAlone', 'CabinFlag', 'SharedTicketCount', 'NormalizedFare']].copy()

    # Some basic cleaning
    X['Embarked'] = X['Embarked'].fillna('Unknown')
    X['Fare'] = X['Fare'].fillna(X['Fare'].median())
    X['NormalizedFare'] = X['NormalizedFare'].fillna(X['NormalizedFare'].median())

    return X, y


if __name__ == '__main__':
    df = load_data()
    X, y = prepare_X_y(df)
    print('Loaded data with', len(X), 'rows; features:', list(X.columns))
import os
import re
import numpy as np
import pandas as pd


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_data(path: str = None) -> pd.DataFrame:
    """Load dataset. By default loads the workspace CSV file in the repo root."""
    if path is None:
        path = os.path.join(_project_root(), 'titanic_cleaned_same_shape.csv')
    return pd.read_csv(path)


def parse_honorific(name: str) -> str:
    """Extract an honorific with a tolerant regex and normalized mapping.

    This function uses a permissive regex, then maps uncommon forms to 'Other'.
    """
    if pd.isna(name):
        return 'Unknown'
    m = re.search(r",\s*([^\.\,]+)\.?\s*", name)
    if m:
        t = m.group(1).strip()
        # normalize some common variants
        mapping = {
            'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs', 'Lady': 'Lady', 'Countess': 'Other'
        }
        return mapping.get(t, t)
    # final fallback
    return 'Other'


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Honorifics
    df['HonorificCode'] = df['Name'].apply(parse_honorific)

    # Family features: family size and a novel "family cohesion" score
    df['FamilySize'] = df.get('SibSp', 0) + df.get('Parch', 0) + 1
    # cohort age variability per shared ticket — smaller variance suggests closer family grouping
    age_std_by_ticket = df.groupby('Ticket')['Age'].transform('std').fillna(0)
    # FamilyCohesion: larger family and low within-ticket age std increases cohesion
    df['FamilyCohesion'] = df['FamilySize'] * np.exp(-0.1 * age_std_by_ticket)

    # Single-traveler flag
    df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

    # Cabin presence flag (named nontrivially)
    df['CabinFlag'] = (~df.get('Cabin', pd.Series([np.nan]*len(df))).isna()).astype(int)

    # Shared ticket count
    df['SharedTicketCount'] = df.groupby('Ticket')['Ticket'].transform('count')

    # Normalized fare per apparent family
    df['NormalizedFare'] = df['Fare'] / df['FamilySize']
    df['NormalizedFare'] = df['NormalizedFare'].replace([np.inf, -np.inf], np.nan)

    # Impute Age sensibly: median per Title, fallback to global median
    age_medians = df.groupby('HonorificCode')['Age'].median()
    global_median = df['Age'].median()

    def impute_age(row):
        if pd.isna(row['Age']):
            t = row['HonorificCode']
            if not pd.isna(age_medians.get(t, np.nan)):
                return age_medians[t]
            return global_median
        return row['Age']

    df['Age'] = df.apply(impute_age, axis=1)

    # Reduce Honorific codes to a short set
    common_titles = ['Mr', 'Mrs', 'Miss', 'Master', 'Dr']
    df['HonorificCode'] = df['HonorificCode'].apply(lambda t: t if t in common_titles else 'Other')

    # Final tidy: select useful columns (keep original columns too)
    # leave downstream code to pick features; return enriched dataframe
    return df


def prepare_X_y(df: pd.DataFrame):
    df = engineer_features(df)
    # Label
    if 'Survived' not in df.columns:
        raise KeyError('Dataset must contain Survived column')
    y = df['Survived'].astype(int)

    # Candidate features (engineered names intentionally distinct)
    X = df[['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'HonorificCode', 'FamilySize', 'FamilyCohesion', 'IsAlone', 'CabinFlag', 'SharedTicketCount', 'NormalizedFare']].copy()

    # Some basic cleaning
    X['Embarked'] = X['Embarked'].fillna('Unknown')
    X['Fare'] = X['Fare'].fillna(X['Fare'].median())
    X['NormalizedFare'] = X['NormalizedFare'].fillna(X['NormalizedFare'].median())

    return X, y


if __name__ == '__main__':
    df = load_data()
    X, y = prepare_X_y(df)
    print('Loaded data with', len(X), 'rows; features:', list(X.columns))
