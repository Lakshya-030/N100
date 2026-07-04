import sqlite3
import pandas as pd
import os

def force_load_excel_to_db():
    db_path = "data/nifty100.db"
    pl_path = "data/raw/profitandloss.xlsx"
    bs_path = "data/raw/balancesheet.xlsx"
    
    print(f"[*] Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # --- CLEAR EXISTING DATA TO PREVENT UNIQUE CONSTRAINT ERRORS ---
    print("[*] Clearing old records from profitandloss and balancesheet...")
    cursor.execute("DELETE FROM profitandloss;")
    cursor.execute("DELETE FROM balancesheet;")
    conn.commit()
    
    # 1. Read and Load Profit & Loss
    if os.path.exists(pl_path):
        print(f"[*] Reading {pl_path}...")
        df_pl = pd.read_excel(pl_path, header=1) # [cite: 162]
        df_pl.columns = df_pl.columns.str.strip().str.lower()
        
        if 'id' in df_pl.columns:
            df_pl = df_pl.drop(columns=['id']) # [cite: 169]
        
        if 'company_id' in df_pl.columns:
            df_pl['company_id'] = df_pl['company_id'].astype(str).str.strip().str.upper() # [cite: 162]
            
        # Drop duplicates in the excel row data itself before loading 
        df_pl = df_pl.drop_duplicates(subset=['company_id', 'year'])
            
        df_pl.to_sql("profitandloss", conn, if_exists="append", index=False)
        print(f"[+] Loaded {len(df_pl)} rows into profitandloss table!")
    else:
        print(f"[!] Critical Error: Cannot find {pl_path}")

    # 2. Read and Load Balance Sheet
    if os.path.exists(bs_path):
        print(f"[*] Reading {bs_path}...")
        df_bs = pd.read_excel(bs_path, header=1) # [cite: 162]
        df_bs.columns = df_bs.columns.str.strip().str.lower()
        
        if 'id' in df_bs.columns:
            df_bs = df_bs.drop(columns=['id']) # [cite: 182]
        
        if 'company_id' in df_bs.columns:
            df_bs['company_id'] = df_bs['company_id'].astype(str).str.strip().str.upper() # [cite: 162]
            
        # Drop duplicates in the excel row data itself before loading 
        df_bs = df_bs.drop_duplicates(subset=['company_id', 'year'])
            
        df_bs.to_sql("balancesheet", conn, if_exists="append", index=False)
        print(f"[+] Loaded {len(df_bs)} rows into balancesheet table!")
    else:
        print(f"[!] Critical Error: Cannot find {bs_path}")

    conn.close()
    print("[+] Force load complete!")

if __name__ == "__main__":
    force_load_excel_to_db()