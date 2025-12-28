# src/data_loading.py
import pandas as pd

def load_csv(file_path):
    """
    Load a CSV file and return a DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {file_path} successfully with shape {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None
