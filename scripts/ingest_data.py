"""
Multi-Format Data Ingestion Script.

Provides explicit CSV loading, nested JSON flattening, encoding fallback strategies,
and detailed audit logging for multi-format pipeline ingestion.
"""

import json
import os
import sys
import pandas as pd

# Reconfigure stdout to UTF-8 to handle checkmarks safely across operating systems
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def resolve_path(filepath: str) -> str:
    """Resolve relative file paths cleanly regardless of execution directory."""
    if os.path.isabs(filepath) or os.path.exists(filepath):
        return filepath
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    candidates = [
        os.path.join(project_root, filepath),
        os.path.join(script_dir, filepath)
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return filepath


def ingest_csv(filepath, delimiter=',', encoding='utf-8', dtype_dict=None):
    """
    Load CSV file with explicit parameters documented.
    
    Args:
        filepath: Path to CSV file
        delimiter: Field delimiter (comma by default, but could be semicolon or tab)
        encoding: File encoding (UTF-8 standard, but may be latin-1 or cp1252)
        dtype_dict: Dictionary mapping column names to data types
    
    Returns:
        Pandas DataFrame with shape and column names confirmed
    """
    path = resolve_path(filepath)
    try:
        df = pd.read_csv(
            path,
            delimiter=delimiter,
            encoding=encoding,
            dtype=dtype_dict
        )
        print(f"✓ CSV loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Columns: {list(df.columns)}")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise
    except UnicodeDecodeError as e:
        print(f"Encoding error: Could not decode with {encoding}")
        print("Try: latin-1, iso-8859-1, or cp1252")
        raise


def ingest_json(filepath, is_nested=False):
    """
    Load JSON file, handling nested structures by flattening them.
    
    Args:
        filepath: Path to JSON file
        is_nested: If True, flatten nested JSON structures into columns
    
    Returns:
        Pandas DataFrame with nested structures expanded
    """
    path = resolve_path(filepath)
    try:
        if is_nested:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.json_normalize(data)
            print("✓ Nested JSON flattened to tabular format")
        else:
            df = pd.read_json(path)
        
        print(f"✓ JSON loaded: {filepath}")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"Error: File not found - {filepath}")
        raise


def ingest_csv_with_fallback(filepath, delimiters=[','], fallback_encodings=None):
    """
    Load CSV with fallback encodings if initial attempt fails.
    
    Tries multiple encodings and delimiters in sequence.
    """
    path = resolve_path(filepath)
    if fallback_encodings is None:
        fallback_encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for delimiter in delimiters:
        for encoding in fallback_encodings:
            try:
                df = pd.read_csv(path, delimiter=delimiter, encoding=encoding)
                print(f"✓ Successfully loaded with delimiter='{delimiter}', encoding='{encoding}'")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    
    raise ValueError(f"Could not load {filepath} with any encoding/delimiter combination")


def document_ingestion(df, source_file):
    """
    Print detailed ingestion report for audit trail.
    """
    print(f"\n{'='*60}")
    print(f"INGESTION REPORT: {source_file}")
    print(f"{'='*60}")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")
    print(f"\nColumn Names & Data Types:")
    print(df.dtypes)
    print(f"\nNull Values Per Column:")
    print(df.isnull().sum())
    print(f"\nFirst 3 Rows:")
    print(df.head(3).to_string())
    print(f"{'='*60}\n")
    return df


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    print("Starting multi-format ingestion...\n")
    
    # Load CSV with explicit parameters
    csv_df = ingest_csv(
        "data/raw/customers.csv",
        delimiter=',',
        encoding='utf-8'
    )
    document_ingestion(csv_df, "customers.csv")
    
    # Load JSON with flattening
    json_df = ingest_json(
        "data/raw/transactions.json",
        is_nested=True
    )
    document_ingestion(json_df, "transactions.json")
    
    # Save ingested data
    cust_out = os.path.join(processed_dir, "customers_ingested.csv")
    txn_out = os.path.join(processed_dir, "transactions_ingested.csv")
    
    csv_df.to_csv(cust_out, index=False)
    json_df.to_csv(txn_out, index=False)
    
    print("\n✓ All data ingested and saved to processed/")
