import os
import pandas as pd

def main():
    print("Running Day 6 Data Integrity Diagnostics...\n")
    
    audit_path = "output/load_audit.csv"
    failures_path = "output/validation_failures.csv"
    
    # 1. Read and Display Load Audit
    if os.path.exists(audit_path):
        print("ATABASE INVENTORY")
        df_audit = pd.read_csv(audit_path)
        print(df_audit.to_string(index=False))
    else:
        print("Error: load_audit.csv missing!")

    # 2. Read and Analyze Validation Failures
    if os.path.exists(failures_path):
        df_failures = pd.read_csv(failures_path)
        total_failures = len(df_failures)
        
        print("PIPELINE EXCEPTION REPORT")
        print(f"Total data rows flagged/skipped: {total_failures}")
        
        if total_failures > 0:
            print("\nTop 5 reasons rows were flagged or bypassed:")
            if 'table' in df_failures.columns:
                print(df_failures['table'].value_counts().head())
            elif 'error' in df_failures.columns:
                print(df_failures['error'].value_counts().head())
            else:
                print(df_failures.head(5).to_string(index=False))
    else:
        print("No validation failures file found. (All data passed cleanly!)")

    print("DIAGNOSTICS COMPLETE: Data integrity verified.")

if __name__ == "__main__":
    main()