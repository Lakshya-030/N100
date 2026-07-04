import sqlite3
import pandas as pd
import numpy as np
import os
import re

def calculate_cagr_value_and_flag(start_val, end_val, num_years):
    """
    Computes the Compounded Annual Growth Rate (CAGR) and handles financial edge cases.
    Returns a tuple of (cagr_value, cagr_flag).
    """
    if start_val is None or end_val is None or pd.isna(start_val) or pd.isna(end_val) or num_years <= 0:
        return None, "INSUFFICIENT"
        
    try:
        start_val = str(start_val).replace(',', '').strip()
        end_val = str(end_val).replace(',', '').strip()
        start_val = float(start_val)
        end_val = float(end_val)
    except:
        return None, "INSUFFICIENT"
    
    if start_val == 0:
        return None, "ZERO_BASE"
        
    if start_val > 0 and end_val > 0:
        cagr = ((end_val / start_val) ** (1 / num_years) - 1) * 100
        return round(cagr, 2), None
        
    if start_val > 0 and end_val <= 0:
        return None, "DECLINE_TO_LOSS"
        
    if start_val < 0 and end_val > 0:
        return None, "TURNAROUND"
        
    if start_val < 0 and end_val <= 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"


def run_production_database_pipeline():
    """
    Main pipeline to fetch financial records, process multi-window growth metrics,
    and persist the structured output into the target database.
    """
    print("--- CAGR Calculation Process Start ---")
    
    db_path = os.path.join("data", "nifty100.db")
    conn = sqlite3.connect(db_path)
    target_table = "profitandloss"
    
    print("Connected to database file successfully.")
    
    raw_df = pd.read_sql_query(f"SELECT * FROM {target_table}", conn)
    print("Total rows fetched from profitandloss table:", len(raw_df))

    raw_df.columns = [col.lower().strip() for col in raw_df.columns]
    
    time_col = 'year'
    rev_col = 'sales'
    pat_col = 'net_profit'
    eps_col = 'eps'

    def extract_year_number(val):
        if pd.isna(val):
            return None
        matches = re.findall(r'\d{4}', str(val))
        if matches:
            return int(matches[0])
        return None

    raw_df['clean_year'] = raw_df[time_col].apply(extract_year_number)
    raw_df = raw_df.dropna(subset=['clean_year'])

    companies = raw_df['company_id'].unique()
    processed_rows = []
    
    for comp in companies:
        comp_df = raw_df[raw_df['company_id'] == comp].copy()
        comp_df = comp_df.sort_values(by='clean_year')
        
        if comp_df.empty:
            continue
            
        latest_row = comp_df.iloc[-1]
        current_year = int(latest_row['clean_year'])
        
        row_result = {
            "company_id": str(comp), 
            "year": str(latest_row[time_col])
        }
        
        for w in [3, 5, 10]:
            target_year = current_year - w
            start_row = comp_df[comp_df['clean_year'] == target_year]
            
            # Revenue Horizon Processing
            val_col, flag_col = f"revenue_cagr_{w}yr", f"revenue_cagr_{w}yr_flag"
            if start_row.empty:
                row_result[val_col], row_result[flag_col] = None, "INSUFFICIENT"
            else:
                val, flag = calculate_cagr_value_and_flag(start_row.iloc[0][rev_col], latest_row[rev_col], w)
                row_result[val_col], row_result[flag_col] = val, flag

            # PAT Horizon Processing
            val_col, flag_col = f"pat_cagr_{w}yr", f"pat_cagr_{w}yr_flag"
            if start_row.empty:
                row_result[val_col], row_result[flag_col] = None, "INSUFFICIENT"
            else:
                val, flag = calculate_cagr_value_and_flag(start_row.iloc[0][pat_col], latest_row[pat_col], w)
                row_result[val_col], row_result[flag_col] = val, flag

            # EPS Horizon Processing
            val_col, flag_col = f"eps_cagr_{w}yr", f"eps_cagr_{w}yr_flag"
            if start_row.empty:
                row_result[val_col], row_result[flag_col] = None, "INSUFFICIENT"
            else:
                val, flag = calculate_cagr_value_and_flag(start_row.iloc[0][eps_col], latest_row[eps_col], w)
                row_result[val_col], row_result[flag_col] = val, flag
                
        processed_rows.append(row_result)
        
    final_df = pd.DataFrame(processed_rows)
    
    final_df.to_sql("company_growth_metrics", conn, if_exists="replace", index=False)
    conn.close()
    
    print("\n--- Final Table Preview ---")
    print(final_df.head(5).to_string(index=False))
    print(f"\nDone! New table 'company_growth_metrics' created with {len(final_df)} companies.")


if __name__ == "__main__":
    run_production_database_pipeline()