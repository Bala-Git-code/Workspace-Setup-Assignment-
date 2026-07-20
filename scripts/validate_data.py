"""
Data Quality & Validation Utility for Incoming Datasets.
"""

import os
import pandas as pd


def validate_csv_schema(file_path: str, required_columns: list) -> bool:
    """
    Validates incoming CSV files for schema completeness and non-empty content.
    
    Args:
        file_path (str): Path to the CSV file to validate.
        required_columns (list): List of expected column names.
        
    Returns:
        bool: True if schema is valid, raises ValueError otherwise.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at path: {file_path}")
        
    df = pd.read_csv(file_path)
    
    if df.empty:
        raise ValueError(f"Dataset at {file_path} is empty.")
        
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in {file_path}: {missing_cols}")
        
    print(f"Validation successful for {file_path}: {len(df)} records verified.")
    return True


if __name__ == "__main__":
    print("Data validation module ready.")
