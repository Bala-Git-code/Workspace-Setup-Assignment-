"""
Data Type Enforcement & Standardization Script.

Enforces strict column data types: converts string dates to datetime64[ns] with explicit formats,
strips currency symbols and converts values to float64, maps binary integer/string flags to boolean,
and exports comparison audit logs.
"""

import os
import sys
import numpy as np
import pandas as pd

# Reconfigure standard output to UTF-8 to handle checkmarks safely across operating systems
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def cast_columns_to_types(df: pd.DataFrame, type_mapping: dict):
    """
    Explicitly cast columns to correct dtypes.
    
    Args:
        df: Input DataFrame
        type_mapping: Dict of {column: target_dtype}
    
    Returns:
        DataFrame with corrected types and conversion log
    """
    df_typed = df.copy()
    conversion_log = {}
    
    for col, target_dtype in type_mapping.items():
        if col not in df.columns:
            print(f"Warning: Column {col} not found in DataFrame")
            continue
        
        original_dtype = df[col].dtype
        
        try:
            df_typed[col] = df_typed[col].astype(target_dtype)
            conversion_log[col] = {
                'from': str(original_dtype),
                'to': str(target_dtype),
                'status': 'success'
            }
            print(f"✓ {col}: {original_dtype} → {target_dtype}")
        except Exception as e:
            conversion_log[col] = {
                'from': str(original_dtype),
                'to': str(target_dtype),
                'status': 'failed',
                'error': str(e)
            }
            print(f"✗ {col}: Conversion failed - {e}")
            raise
    
    return df_typed, conversion_log


def convert_string_dates_to_datetime(df: pd.DataFrame, date_columns: list, date_format: str = None) -> pd.DataFrame:
    """
    Convert string columns to datetime with explicit format.
    
    Args:
        df: Input DataFrame
        date_columns: List of column names containing dates
        date_format: Datetime format string (e.g., '%Y-%m-%d')
    
    Returns:
        DataFrame with datetime columns converted
    """
    df_typed = df.copy()
    
    for col in date_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
        
        try:
            if date_format:
                df_typed[col] = pd.to_datetime(df_typed[col], format=date_format)
            else:
                df_typed[col] = pd.to_datetime(df_typed[col])
            
            print(f"✓ {col}: Converted to datetime")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            print(f"  Sample values: {df[col].head(3).tolist()}")
            print(f"  Expected format: {date_format}")
            raise
    
    return df_typed


def convert_currency_to_float(df: pd.DataFrame, currency_columns: list) -> pd.DataFrame:
    """
    Strip currency symbols and convert to float.
    
    Example: '$150.50' → 150.50
    
    Args:
        df: Input DataFrame
        currency_columns: List of column names with currency
    
    Returns:
        DataFrame with clean numeric columns
    """
    df_typed = df.copy()
    
    for col in currency_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
        
        try:
            df_typed[col] = (df_typed[col]
                            .astype(str)
                            .str.replace(r'[$,]', '', regex=True)
                            .str.strip())
            
            df_typed[col] = pd.to_numeric(df_typed[col], errors='coerce')
            
            failed_conversions = df_typed[col].isnull().sum() - df[col].isnull().sum()
            if failed_conversions > 0:
                print(f"⚠ {col}: {failed_conversions} values could not be converted to numeric")
            
            print(f"✓ {col}: Stripped symbols, converted to float")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            raise
    
    return df_typed


def convert_integers_to_boolean(df: pd.DataFrame, boolean_columns: list) -> pd.DataFrame:
    """
    Convert 0/1 or yes/no columns to proper boolean type.
    
    Args:
        df: Input DataFrame
        boolean_columns: List of column names with binary values
    
    Returns:
        DataFrame with bool columns
    """
    df_typed = df.copy()
    
    for col in boolean_columns:
        if col not in df.columns:
            print(f"Warning: Column {col} not found")
            continue
        
        try:
            unique_vals = df[col].unique()
            print(f"  {col} unique values: {unique_vals}")
            
            if df[col].dtype == 'object':
                mapping = {
                    'yes': True, 'no': False,
                    'y': True, 'n': False,
                    'true': True, 'false': False,
                    '1': True, '0': False,
                    1: True, 0: False,
                    True: True, False: False
                }
                df_typed[col] = df_typed[col].map(mapping).astype(bool)
            else:
                df_typed[col] = df_typed[col].astype(bool)
            
            print(f"✓ {col}: Converted to boolean")
            
        except Exception as e:
            print(f"✗ {col}: Conversion failed - {e}")
            raise
    
    return df_typed


def compare_dtypes(df_original: pd.DataFrame, df_typed: pd.DataFrame, output_path: str = 'output/dtype_conversion_report.csv') -> pd.DataFrame:
    """
    Compare dtypes before and after conversion.
    
    Returns: Summary of all changes
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    resolved_out = output_path
    if not os.path.isabs(output_path):
        resolved_out = os.path.join(project_root, output_path)
        
    os.makedirs(os.path.dirname(resolved_out), exist_ok=True)
    
    comparison = pd.DataFrame({
        'column': df_original.columns,
        'dtype_before': df_original.dtypes.values,
        'dtype_after': df_typed.dtypes.values,
        'changed': (df_original.dtypes != df_typed.dtypes).values
    })
    
    print("\n" + "="*70)
    print("DTYPE CONVERSION SUMMARY")
    print("="*70)
    print(comparison.to_string(index=False))
    
    comparison.to_csv(resolved_out, index=False)
    print(f"\nReport saved to {output_path}")
    print("="*70)
    
    return comparison


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    raw_path = os.path.join(project_root, "data", "raw", "untyped_data.csv")
    df = pd.read_csv(raw_path)
    
    print("="*70)
    print("BEFORE TYPE CONVERSION")
    print("="*70)
    print(df.dtypes)
    print(f"\nSample data:")
    print(df.head(3))
    
    df_typed = df.copy()
    
    print("\n1. Converting date columns...")
    date_cols = [c for c in ['transaction_date', 'signup_date'] if c in df_typed.columns]
    if date_cols:
        df_typed = convert_string_dates_to_datetime(
            df_typed,
            date_cols,
            date_format='%Y-%m-%d'
        )
    
    print("\n2. Converting currency columns...")
    curr_cols = [c for c in ['amount', 'revenue'] if c in df_typed.columns]
    if curr_cols:
        df_typed = convert_currency_to_float(
            df_typed,
            curr_cols
        )
    
    print("\n3. Converting boolean columns...")
    bool_cols = [c for c in ['is_active', 'is_premium'] if c in df_typed.columns]
    if bool_cols:
        df_typed = convert_integers_to_boolean(
            df_typed,
            bool_cols
        )
    
    print("\n4. Comparing before/after types...")
    print("="*70)
    print("AFTER TYPE CONVERSION")
    print("="*70)
    print(df_typed.dtypes)
    print(f"\nSample data:")
    print(df_typed.head(3))
    
    compare_dtypes(df, df_typed)
    
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    out_csv = os.path.join(processed_dir, "typed_data.csv")
    df_typed.to_csv(out_csv, index=False)
    print("\n✓ Typed data saved to data/processed/typed_data.csv")
