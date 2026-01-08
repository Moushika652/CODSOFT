def add_features(df):
    df = df.copy()
    if 'Votes' in df.columns and 'Rating' in df.columns:
        df['Votes_Rating'] = df['Votes'] * df['Rating']
    return df
