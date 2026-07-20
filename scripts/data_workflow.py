"""
Production-Ready Data Processing Workflow Script.

This module establishes a modular data pipeline that ingests raw transaction datasets,
applies cleaning and feature transformations, and exports analysis-ready output datasets.
Designed for command-line execution and automated CI/CD pipelines.
"""

import os
import sys
import pandas as pd

# Reconfigure standard output to UTF-8 to handle checkmark characters safely on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def ingest_data(filepath: str) -> pd.DataFrame:
    """
    Load raw tabular data from a file (CSV or JSON) into a Pandas DataFrame.

    What it does:
        Verifies the existence of the source file and loads its contents into memory
        as a structured DataFrame.

    Input:
        filepath (str): Relative or absolute path to the input CSV/JSON file.

    Returns:
        pd.DataFrame: Loaded raw dataset.

    Assumptions & Constraints:
        - Expects a valid, accessible file path.
        - File must be UTF-8 encoded CSV or JSON format.
        - Raises FileNotFoundError if the path does not exist.
    """
    # Handle relative path resolution from script location or workspace root
    if not os.path.isabs(filepath):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, ".."))
        possible_paths = [
            os.path.abspath(filepath),
            os.path.join(project_root, filepath),
            os.path.join(script_dir, filepath)
        ]
        resolved_path = None
        for path in possible_paths:
            if os.path.exists(path):
                resolved_path = path
                break
        if not resolved_path:
            raise FileNotFoundError(f"Input data file not found at any of: {possible_paths}")
        filepath = resolved_path

    # Read data based on file extension
    if filepath.endswith('.json'):
        df = pd.read_json(filepath)
    else:
        df = pd.read_csv(filepath)

    return df


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw transaction data into a clean, analysis-ready format.

    What it does:
        - Removes duplicate records across all columns.
        - Imputes missing numerical values (e.g., transaction amount) using column median.
        - Standardizes text columns to uppercase formatting.
        - Calculates a derived column for total transaction cost including estimated tax.

    Input:
        df (pd.DataFrame): Raw DataFrame containing transaction data.

    Returns:
        pd.DataFrame: Cleaned and enriched DataFrame.

    Assumptions & Constraints:
        - Input DataFrame contains standard tabular columns.
        - Numerical columns requiring imputation have at least one valid non-null value.
    """
    # Step 1: Remove exact duplicate rows across all columns
    df_clean = df.drop_duplicates().copy()

    # Step 2: Fill missing values in numerical columns with column median
    num_cols = df_clean.select_dtypes(include=['number']).columns
    for col in num_cols:
        if df_clean[col].isnull().any():
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)

    # Step 3: Standardize string column values (strip whitespace and upper-case status)
    if 'status' in df_clean.columns:
        df_clean['status'] = df_clean['status'].astype(str).str.strip().str.upper()

    # Step 4: Add a derived column for total amount including 8% tax calculation
    if 'amount' in df_clean.columns:
        df_clean['amount_with_tax'] = (df_clean['amount'] * 1.08).round(2)

    return df_clean


def output_results(df: pd.DataFrame, output_path: str) -> None:
    """
    Export processed DataFrame to a CSV destination file and print confirmation metrics.

    What it does:
        - Creates parent directories if they do not exist.
        - Writes the DataFrame to disk as a CSV file without index numbers.
        - Displays user-friendly confirmation metrics to standard output.

    Input:
        df (pd.DataFrame): Processed DataFrame to export.
        output_path (str): Filepath destination for the processed CSV output.

    Returns:
        None

    Assumptions & Constraints:
        - Requires write permissions for the specified output directory path.
    """
    # Ensure target output directory exists before writing
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save processed DataFrame to CSV
    df.to_csv(output_path, index=False)

    # Print execution confirmation summary
    print(f"✓ Data successfully processed")
    print(f"✓ Rows processed: {len(df)}")
    print(f"✓ Output saved to {output_path}")


if __name__ == "__main__":
    # Define input and output file paths relative to project root
    input_file = "data/raw/sample.csv"
    output_file = "output/processed.csv"

    # Orchestrate pipeline execution stages
    data = ingest_data(input_file)
    processed = process_data(data)
    output_results(processed, output_file)
