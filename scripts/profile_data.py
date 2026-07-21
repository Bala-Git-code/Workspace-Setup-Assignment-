"""
Data Profiling & Quality Assessment Script.

Computes null percentages, exact duplicates, numerical distributions, categorical value
frequencies, and flags quality issues to generate a structured JSON quality report.
"""

import json
import os
import sys
import numpy as np
import pandas as pd

# Reconfigure standard output to UTF-8 to handle special characters cleanly across operating systems
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def resolve_path(filepath: str) -> str:
    """Resolve relative file paths cleanly regardless of execution context."""
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


def profile_nulls_and_duplicates(df: pd.DataFrame) -> dict:
    """
    Compute null percentage and duplicate counts per column.
    
    Returns: Dictionary with null analysis by column
    """
    profile = {
        'null_counts': {},
        'null_percentages': {},
        'exact_duplicate_count': 0
    }
    
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = (null_count / len(df)) * 100 if len(df) > 0 else 0.0
        profile['null_counts'][col] = null_count
        profile['null_percentages'][col] = round(null_pct, 2)
    
    dup_count = int(df.duplicated().sum())
    profile['exact_duplicate_count'] = dup_count
    profile['duplicate_percentage'] = round((dup_count / len(df)) * 100, 2) if len(df) > 0 else 0.0
    
    return profile


def profile_numerical_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarise numerical columns with statistical measures.
    
    Returns: DataFrame with min, max, mean, median, std
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    stats = {}
    for col in numerical_cols:
        valid_series = df[col].dropna()
        if len(valid_series) > 0:
            stats[col] = {
                'min': round(float(df[col].min()), 2),
                'max': round(float(df[col].max()), 2),
                'mean': round(float(df[col].mean()), 2),
                'median': round(float(df[col].median()), 2),
                'std': round(float(df[col].std()), 2) if len(valid_series) > 1 else 0.0,
                'null_count': int(df[col].isnull().sum())
            }
        else:
            stats[col] = {
                'min': None,
                'max': None,
                'mean': None,
                'median': None,
                'std': None,
                'null_count': int(df[col].isnull().sum())
            }
    
    return pd.DataFrame(stats).T


def profile_categorical_columns(df: pd.DataFrame, top_n: int = 5) -> dict:
    """
    Summarise categorical columns with value distributions.
    
    Returns: Dictionary with unique counts and top values
    """
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    profile = {}
    for col in categorical_cols:
        profile[col] = {
            'unique_count': int(df[col].nunique()),
            'top_values': df[col].value_counts().head(top_n).to_dict(),
            'null_count': int(df[col].isnull().sum())
        }
    
    return profile


def identify_quality_issues(df: pd.DataFrame, null_threshold: float = 30.0, duplicate_threshold: float = 5.0) -> list:
    """
    Identify data quality problems based on thresholds.
    
    Returns: List of issues found with severity and recommendations
    """
    issues = []
    
    # Check nulls
    null_pcts = (df.isnull().sum() / len(df)) * 100 if len(df) > 0 else df.isnull() * 0
    for col, pct in null_pcts.items():
        if pct > null_threshold:
            issues.append({
                'type': 'High nulls',
                'column': col,
                'severity': 'HIGH',
                'value': f"{pct:.1f}% missing",
                'recommendation': 'Consider imputation or column exclusion'
            })
    
    # Check duplicates
    dup_count = df.duplicated().sum()
    dup_pct = (dup_count / len(df)) * 100 if len(df) > 0 else 0.0
    if dup_pct > duplicate_threshold:
        issues.append({
            'type': 'High duplicates',
            'column': 'Full row',
            'severity': 'HIGH',
            'value': f"{dup_pct:.1f}% duplicated",
            'recommendation': 'Deduplication required before analysis'
        })
    
    # Check for invalid ranges
    for col in df.select_dtypes(include=[np.number]).columns:
        if (df[col] < 0).any() and 'amount' in col.lower():
            issues.append({
                'type': 'Invalid range',
                'column': col,
                'severity': 'MEDIUM',
                'value': 'Contains negative values',
                'recommendation': 'Investigate negative entries'
            })
    
    return issues


def generate_profile_report(df: pd.DataFrame, filepath: str, output_path: str = 'output/profile_report.json') -> dict:
    """
    Generate complete data quality report and save to JSON.
    
    Returns: Complete profile report dictionary
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    resolved_out = output_path
    if not os.path.isabs(output_path):
        resolved_out = os.path.join(project_root, output_path)
    
    out_dir = os.path.dirname(resolved_out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    report = {
        'dataset': filepath,
        'record_count': len(df),
        'column_count': len(df.columns),
        'nulls_and_duplicates': profile_nulls_and_duplicates(df),
        'numerical_stats': profile_numerical_columns(df).to_dict(),
        'categorical_stats': profile_categorical_columns(df),
        'quality_issues': identify_quality_issues(df)
    }
    
    # Save report
    with open(resolved_out, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"DATA QUALITY PROFILE: {filepath}")
    print(f"{'='*60}")
    print(f"Records: {report['record_count']}")
    print(f"Columns: {report['column_count']}")
    print(f"\nQuality Issues Found: {len(report['quality_issues'])}")
    for issue in report['quality_issues']:
        print(f"  [{issue['severity']}] {issue['type']} in {issue['column']}")
        print(f"    Value: {issue['value']} → {issue['recommendation']}")
    print(f"{'='*60}\n")
    
    return report


if __name__ == "__main__":
    filepath = "data/raw/quality_test.csv"
    resolved_file = resolve_path(filepath)
    df = pd.read_csv(resolved_file)
    generate_profile_report(df, filepath)
