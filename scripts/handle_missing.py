"""
Missing Value Treatment and Imputation Module.

Computes null metrics prior to treatment, applies domain-specific imputation strategies
(row dropping, median imputation, mode fill, forward fill), logs decision rationale,
and validates before/after dataset completeness.
"""

import json
import os
import sys
import numpy as np
import pandas as pd

# Reconfigure standard output to UTF-8 to handle checkmark symbols cleanly across platforms
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute null counts and percentages before treatment.
    
    Returns: DataFrame with analysis of missing data by column
    """
    missing_analysis = pd.DataFrame({
        'column': df.columns,
        'null_count': df.isnull().sum().values,
        'null_percentage': (df.isnull().sum() / len(df) * 100).round(2).values if len(df) > 0 else 0.0,
        'data_type': df.dtypes.values,
        'null_meaning': ''  # To be filled based on column context
    })
    
    print("="*70)
    print("BEFORE IMPUTATION - Missing Value Analysis")
    print("="*70)
    print(missing_analysis.to_string(index=False))
    print(f"\nTotal rows: {len(df)}")
    print(f"Total cells: {len(df) * len(df.columns)}")
    print(f"Missing cells: {df.isnull().sum().sum()}")
    print("="*70)
    
    return missing_analysis


def impute_mean_median(df: pd.DataFrame, numerical_cols: list, strategy: str = 'median') -> pd.DataFrame:
    """Fill numerical nulls with mean or median."""
    df_imputed = df.copy()
    for col in numerical_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            null_count = int(df[col].isnull().sum())
            fill_value = df[col].median() if strategy == 'median' else df[col].mean()
            df_imputed[col] = df_imputed[col].fillna(fill_value)
            print(f"  ✓ {col}: filled {null_count} nulls with {strategy} ({fill_value:.2f})")
    return df_imputed


def impute_mode(df: pd.DataFrame, categorical_cols: list) -> pd.DataFrame:
    """Fill categorical nulls with mode (most common value)."""
    df_imputed = df.copy()
    for col in categorical_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            null_count = int(df[col].isnull().sum())
            modes = df[col].mode()
            mode_val = modes[0] if len(modes) > 0 else 'UNKNOWN'
            df_imputed[col] = df_imputed[col].fillna(mode_val)
            print(f"  ✓ {col}: filled {null_count} nulls with mode '{mode_val}'")
    return df_imputed


def impute_forward_fill(df: pd.DataFrame, time_series_cols: list) -> pd.DataFrame:
    """Fill with previous value (for time-series data)."""
    df_imputed = df.copy()
    for col in time_series_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            null_count = int(df[col].isnull().sum())
            df_imputed[col] = df_imputed[col].ffill()
            print(f"  ✓ {col}: forward-filled {null_count} nulls")
    return df_imputed


def drop_rows_with_nulls(df: pd.DataFrame, critical_cols: list) -> pd.DataFrame:
    """Drop rows where critical columns are null."""
    existing_critical = [col for col in critical_cols if col in df.columns]
    rows_before = len(df)
    df_imputed = df.dropna(subset=existing_critical)
    rows_dropped = rows_before - len(df_imputed)
    print(f"  ✓ Dropped {rows_dropped} rows with null in: {existing_critical}")
    return df_imputed


def document_imputation_decisions(df_original: pd.DataFrame, df_imputed: pd.DataFrame, output_path: str = 'output/imputation_decisions.json') -> dict:
    """Document all imputation decisions with business justification."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    resolved_out = output_path
    if not os.path.isabs(output_path):
        resolved_out = os.path.join(project_root, output_path)
        
    os.makedirs(os.path.dirname(resolved_out), exist_ok=True)
    
    decisions = {
        'amount': {
            'column_type': 'numerical',
            'null_count_before': int(df_original['amount'].isnull().sum()) if 'amount' in df_original else 0,
            'strategy': 'median_imputation',
            'value_used': float(df_original['amount'].median()) if 'amount' in df_original and not df_original['amount'].dropna().empty else None,
            'business_reasoning': 'Median purchase amount is representative of typical transaction. Mean would be skewed by high-value outliers. Maintains distribution integrity.',
            'risk_assessment': 'Low - median is stable metric resistant to outliers'
        },
        'email': {
            'column_type': 'categorical_identifier',
            'null_count_before': int(df_original['email'].isnull().sum()) if 'email' in df_original else 0,
            'strategy': 'drop_rows',
            'rows_affected': int(df_original['email'].isnull().sum()) if 'email' in df_original else 0,
            'business_reasoning': 'Email is critical for customer contact and marketing campaigns. Rows without email cannot be used for outreach. Data is incomplete.',
            'risk_assessment': 'Low - only affects small percentage of data'
        },
        'customer_id': {
            'column_type': 'primary_key',
            'null_count_before': int(df_original['customer_id'].isnull().sum()) if 'customer_id' in df_original else 0,
            'strategy': 'drop_rows',
            'rows_affected': int(df_original['customer_id'].isnull().sum()) if 'customer_id' in df_original else 0,
            'business_reasoning': 'Customer ID is primary identifier. Records missing customer IDs cannot be linked to customer accounts.',
            'risk_assessment': 'Low - preserves entity integrity'
        },
        'category': {
            'column_type': 'categorical',
            'null_count_before': int(df_original['category'].isnull().sum()) if 'category' in df_original else 0,
            'strategy': 'mode_imputation',
            'value_used': str(df_original['category'].mode()[0]) if 'category' in df_original and not df_original['category'].dropna().empty else 'UNKNOWN',
            'business_reasoning': 'Category missing values are imputed with the most frequent category (mode) to preserve classification consistency.',
            'risk_assessment': 'Low - mode represents standard default category'
        },
        'status_date': {
            'column_type': 'datetime_series',
            'null_count_before': int(df_original['status_date'].isnull().sum()) if 'status_date' in df_original else 0,
            'strategy': 'forward_fill',
            'interpretation': 'Assumes last known status date is still valid until changed',
            'business_reasoning': 'For time-series analysis, forward fill preserves temporal continuity. Status typically does not change frequently.',
            'risk_assessment': 'Medium - assumes no change between observations'
        }
    }
    
    with open(resolved_out, 'w', encoding='utf-8') as f:
        json.dump(decisions, f, indent=2, default=str)
    
    return decisions


def validate_imputation(df_original: pd.DataFrame, df_imputed: pd.DataFrame) -> pd.DataFrame:
    """Compare metrics before and after imputation."""
    print("\n" + "="*70)
    print("AFTER IMPUTATION - Validation Report")
    print("="*70)
    print(f"Total rows before: {len(df_original)}")
    print(f"Total rows after:  {len(df_imputed)}")
    print(f"Rows removed: {len(df_original) - len(df_imputed)}")
    print(f"\nTotal nulls before: {df_original.isnull().sum().sum()}")
    print(f"Total nulls after:  {df_imputed.isnull().sum().sum()}")
    
    missing_after = pd.DataFrame({
        'column': df_imputed.columns,
        'null_count_after': df_imputed.isnull().sum().values,
        'null_percentage_after': (df_imputed.isnull().sum() / len(df_imputed) * 100).round(2).values if len(df_imputed) > 0 else 0.0
    })
    
    print("\nNull values by column after imputation:")
    print(missing_after.to_string(index=False))
    print("="*70)
    
    return missing_after


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    raw_path = os.path.join(project_root, "data", "raw", "missing_data.csv")
    if not os.path.exists(raw_path):
        raw_path = os.path.join(project_root, "data", "raw", "raw_data.csv")
        
    df_original = pd.read_csv(raw_path)
    
    # Step 1: Analyze missing before treatment
    print("Step 1: Analyzing missing values...")
    analyze_missing_values(df_original)
    
    # Step 2: Apply strategy-specific imputation
    print("\nStep 2: Applying imputation strategies...")
    
    # Drop rows with nulls in critical columns
    df_cleaned = drop_rows_with_nulls(df_original, ['customer_id', 'email'])
    
    # Impute numerical columns
    num_cols = [c for c in ['amount', 'quantity'] if c in df_cleaned.columns]
    if num_cols:
        df_cleaned = impute_mean_median(df_cleaned, num_cols, strategy='median')
    
    # Impute categorical columns
    cat_cols = [c for c in ['name', 'category', 'region'] if c in df_cleaned.columns]
    if cat_cols:
        df_cleaned = impute_mode(df_cleaned, cat_cols)
    
    # Impute time-series columns
    ts_cols = [c for c in ['last_updated', 'status_date'] if c in df_cleaned.columns]
    if ts_cols:
        df_cleaned = impute_forward_fill(df_cleaned, ts_cols)
    
    # Step 3: Document decisions
    print("\nStep 3: Documenting imputation decisions...")
    document_imputation_decisions(df_original, df_cleaned)
    
    # Step 4: Validate results
    print("\nStep 4: Validating imputation...")
    validate_imputation(df_original, df_cleaned)
    
    # Save cleaned data
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    out_csv = os.path.join(processed_dir, "cleaned_data.csv")
    df_cleaned.to_csv(out_csv, index=False)
    print("\n✓ Cleaned data saved to data/processed/cleaned_data.csv")
