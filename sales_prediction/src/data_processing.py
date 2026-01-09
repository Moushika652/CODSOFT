import pandas as pd
import numpy as np

def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_data(df):
    df = df.copy()
    
    if df is None or df.empty:
        return df
    
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].fillna('Unknown')
        else:
            df[col] = df[col].fillna(df[col].median())
    
    return df

def prepare_features(df):
    df = clean_data(df)
    
    if 'Sales' not in df.columns:
        return None, None
    
    feature_cols = [col for col in df.columns if col != 'Sales']
    X = df[feature_cols].select_dtypes(include=[np.number])
    y = df['Sales']
    
    return X, y
