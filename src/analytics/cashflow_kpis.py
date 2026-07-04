import sqlite3
import pandas as pd
import numpy as np
import os

def calculate_free_cash_flow(operating_activity, investing_activity):
    cfo = operating_activity if operating_activity is not None else 0.0
    cfi = investing_activity if investing_activity is not None else 0.0
    return round(cfo + cfi, 2)

def classify_cfo_quality(cfo_quality_score):
    if cfo_quality_score is None:
        return None
    if cfo_quality_score > 1.0:
        return "High Quality"
    elif 0.5 <= cfo_quality_score <= 1.0:
        return "Moderate"
    else:
        return "Accrual Risk"

def calculate_capex_intensity(investing_activity, sales):
    if sales <= 0:
        return 0.0, "Asset Light"
    cfi = investing_activity if investing_activity is not None else 0.0
    intensity_pct = (abs(cfi) / sales) * 100
    if intensity_pct < 3.0:
        label = "Asset Light"
    elif 3.0 <= intensity_pct <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return round(intensity_pct, 2), label

def calculate_fcf_conversion_rate(fcf, operating_profit):
    if operating_profit == 0:
        return None
    return round((fcf / operating_profit) * 100, 2)

def classify_capital_allocation(cfo, cfi, cff, cfo_quality_score):
    cfo_sign = "+" if cfo >= 0 else "-"
    cfi_sign = "+" if cfi >= 0 else "-"
    cff_sign = "+" if cff >= 0 else "-"
    
    if cfo_sign == "+" and cfi_sign == "-" and cff_sign == "-":
        if cfo_quality_score is not None and cfo_quality_score > 1.0:
            return "Shareholder Returns"
        return "Reinvestor"
    elif cfo_sign == "+" and cfi_sign == "+" and cff_sign == "-":
        return "Liquidating Assets"
    elif cfo_sign == "-" and cfi_sign == "+" and cff_sign == "+":
        return "Distress Signal"
    elif cfo_sign == "-" and cfi_sign == "-" and cff_sign == "+":
        return "Growth Funded by Debt"
    elif cfo_sign == "+" and cfi_sign == "+" and cff_sign == "+":
        return "Cash Accumulator"
    elif cfo_sign == "-" and cfi_sign == "-" and cff_sign == "-":
        return "Pre-Revenue"
    elif cfo_sign == "+" and cfi_sign == "-" and cff_sign == "+":
        return "Mixed"
    return "Mixed"

def run_cashflow_pipeline():
    print("--- Day 11: Processing Real Cash Flow Pipeline ---")
    
    db_path = os.path.join("data", "nifty100.db")
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    
    cf_df = pd.read_sql_query("SELECT * FROM cashflow", conn)
    pl_df = pd.read_sql_query("SELECT * FROM profitandloss", conn)
    
    cf_df.columns = [col.lower().strip() for col in cf_df.columns]
    pl_df.columns = [col.lower().strip() for col in pl_df.columns]
    
    # Year safe parse block to prevent row drops
    cf_df['year_str'] = cf_df['year'].astype(str).str.strip()
    pl_df['year_str'] = pl_df['year'].astype(str).str.strip()
    
    cf_df['year_clean'] = cf_df['year_str'].str.extract(r'(\d{4})')[0].fillna(cf_df['year_str'])
    pl_df['year_clean'] = pl_df['year_str'].str.extract(r'(\d{4})')[0].fillna(pl_df['year_str'])
    
    cf_df['year'] = pd.to_numeric(cf_df['year_clean'], errors='coerce')
    pl_df['year'] = pd.to_numeric(pl_df['year_clean'], errors='coerce')
    
    cf_df = cf_df.dropna(subset=['year', 'company_id'])
    pl_df = pl_df.dropna(subset=['year', 'company_id'])
    
    cf_df['year'] = cf_df['year'].astype(int)
    pl_df['year'] = pl_df['year'].astype(int)
    
    cf_df = cf_df.drop(columns=['year_clean', 'year_str'])
    pl_df = pl_df.drop(columns=['year_clean', 'year_str'])
    
    cf_df['company_id'] = cf_df['company_id'].astype(str).str.strip().str.upper()
    pl_df['company_id'] = pl_df['company_id'].astype(str).str.strip().str.upper()
    
    print(f"[INFO] Raw Cashflow rows inside database: {len(cf_df)}")
    print(f"[INFO] Raw Profit&Loss rows inside database: {len(pl_df)}")
    
    merged_df = pd.merge(cf_df, pl_df, on=['company_id', 'year'], how='outer')
    print(f"[INFO] Merged dataframe rows: {len(merged_df)}")
    
    numeric_cols = ['operating_activity', 'investing_activity', 'financing_activity', 'sales', 'net_profit', 'operating_profit']
    for col in numeric_cols:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        else:
            merged_df[col] = 0.0

    processed_rows = []
    companies = merged_df['company_id'].dropna().unique()
    
    for comp in companies:
        comp_df = merged_df[merged_df['company_id'] == comp].sort_values(by='year')
        
        comp_df['cfo_pat_ratio'] = np.where(comp_df['net_profit'] == 0, 0.0, comp_df['operating_activity'] / comp_df['net_profit'])
        comp_df['cfo_quality_5yr'] = comp_df['cfo_pat_ratio'].rolling(window=5, min_periods=1).mean()
        
        for idx, row in comp_df.iterrows():
            cfo = row['operating_activity']
            cfi = row['investing_activity']
            cff = row['financing_activity']
            cfo_quality = row['cfo_quality_5yr']
            
            pattern = classify_capital_allocation(cfo, cfi, cff, cfo_quality)
            
            processed_rows.append({
                "company_id": row['company_id'],
                "year": row['year'],
                "cfo_sign": "+" if cfo >= 0 else "-",
                "cfi_sign": "+" if cfi >= 0 else "-",
                "cff_sign": "+" if cff >= 0 else "-",
                "pattern_label": pattern
            })
            
    final_df = pd.DataFrame(processed_rows)
    
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "capital_allocation.csv")
    final_df.to_csv(output_path, index=False)
    
    print(f"[SUCCESS] CSV Exported perfectly with {len(final_df)} rows at: {output_path}")
    conn.close()

if __name__ == "__main__":
    run_cashflow_pipeline()