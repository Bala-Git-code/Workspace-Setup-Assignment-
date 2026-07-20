"""
Dataset Intake Validation & Quality Firewall Script.

This module validates raw incoming datasets for file existence, format support,
schema completeness, character encoding, and baseline dimension statistics.
Generates a structured JSON validation report to gate downstream pipeline execution.
"""

import json
import os
import sys
from datetime import datetime
import chardet
import pandas as pd

# Reconfigure stdout to UTF-8 for clean console printing across operating systems
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def validate_file_exists(filepath: str):
    """Check if file exists and is non-empty."""
    if not os.path.exists(filepath):
        return False, f"File does not exist: {filepath}"
    
    if os.path.getsize(filepath) == 0:
        return False, f"File is empty: {filepath}"
    
    return True, "File exists and has content"


def validate_file_format(filepath: str, allowed_formats=['csv', 'json', 'xlsx']):
    """Check if file extension is supported."""
    extension = filepath.split('.')[-1].lower()
    
    if extension not in allowed_formats:
        return False, f"Unsupported format: {extension}. Allowed: {allowed_formats}"
    
    return True, f"Format valid: {extension}"


def validate_schema(df: pd.DataFrame, expected_columns: list):
    """Validate that DataFrame has all expected columns."""
    missing = set(expected_columns) - set(df.columns)
    extra = set(df.columns) - set(expected_columns)
    
    issues = []
    if missing:
        issues.append(f"Missing columns: {missing}")
    if extra:
        issues.append(f"Unexpected columns: {extra}")
    
    if not issues:
        return True, f"Schema valid: {len(df.columns)} columns present"
    return False, " | ".join(issues)


def detect_encoding(filepath: str):
    """Detect file encoding with confidence using chardet."""
    with open(filepath, 'rb') as f:
        result = chardet.detect(f.read(10000))
    
    raw_encoding = result.get('encoding', 'utf-8')
    encoding = raw_encoding.lower() if raw_encoding else 'utf-8'
    confidence = result.get('confidence', 0.0) if result.get('confidence') else 0.0
    
    return encoding, f"Detected: {encoding} (confidence: {confidence:.1%})"


def capture_dataset_stats(filepath: str, df: pd.DataFrame):
    """Log row count, column count, byte size, and megabyte size."""
    bytes_size = os.path.getsize(filepath)
    file_size_mb = bytes_size / (1024 * 1024)
    row_count = len(df)
    col_count = len(df.columns)
    
    return {
        'rows': row_count,
        'columns': col_count,
        'file_size_mb': round(file_size_mb, 5) if file_size_mb < 0.01 else round(file_size_mb, 2),
        'bytes': bytes_size
    }


def generate_intake_report(filepath: str, expected_columns: list, report_path: str = 'output/intake_report.json'):
    """Generate complete intake validation report and write to JSON."""
    # Resolve relative paths cleanly regardless of working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    resolved_filepath = filepath
    if not os.path.isabs(filepath):
        possible_input_paths = [
            os.path.abspath(filepath),
            os.path.join(project_root, filepath),
            os.path.join(script_dir, filepath)
        ]
        for p in possible_input_paths:
            if os.path.exists(p):
                resolved_filepath = p
                break

    resolved_report_path = report_path
    if not os.path.isabs(report_path):
        resolved_report_path = os.path.join(project_root, report_path)

    report = {
        'timestamp': datetime.now().isoformat(),
        'filepath': filepath,
        'validations': {}
    }
    
    # Step 1: Check existence and non-emptiness
    file_exists, msg = validate_file_exists(resolved_filepath)
    report['validations']['file_exists'] = msg
    if not file_exists:
        print(f"❌ Validation Failed: {msg}")
        return report
    
    # Step 2: Check format
    format_valid, msg = validate_file_format(resolved_filepath)
    report['validations']['format'] = msg
    if not format_valid:
        print(f"❌ Validation Failed: {msg}")
        return report

    # Step 3: Check encoding
    encoding, msg = detect_encoding(resolved_filepath)
    report['validations']['encoding'] = msg
    
    # Step 4: Load data for schema validation & statistics
    try:
        df = pd.read_csv(resolved_filepath, encoding=encoding if encoding != 'ascii' else 'utf-8')
    except Exception:
        df = pd.read_csv(resolved_filepath)
    
    # Step 5: Check schema
    schema_valid, msg = validate_schema(df, expected_columns)
    report['validations']['schema'] = msg
    
    # Step 6: Capture statistics
    stats = capture_dataset_stats(resolved_filepath, df)
    report['statistics'] = stats

    # Ensure output directory exists and save report
    out_dir = os.path.dirname(resolved_report_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    with open(resolved_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"✓ Intake Validation Complete")
    print(f"✓ Report written to: {report_path}")
    print(json.dumps(report, indent=2))
    
    return report


if __name__ == "__main__":
    filepath = "data/raw/sample.csv"
    expected_columns = [
        "customer_id",
        "customer_name",
        "transaction_amount",
        "transaction_date"
    ]
    generate_intake_report(filepath, expected_columns)
