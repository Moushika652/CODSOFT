# src/feature_engineering.py

def add_features(df):
    """
    Add new features to the dataset.
    Example: create a feature based on existing columns.
    """
    df = df.copy()
    # Example: interaction feature
    if 'Votes' in df.columns and 'Rating' in df.columns:
        df['Votes_Rating'] = df['Votes'] * df['Rating']
    return df
