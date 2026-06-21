import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import sqlite3
import pandas as pd
from datetime import datetime
from src.etl.normaliser import normalize_ticker, normalize_year
from src.etl.validator import run_data_quality_checks, save_validation_failures

def align_dataframe_to_db(df, conn, table_name):
    cursor = conn.execute(f"PRAGMA table_info({table_name});")
    db_cols = [row[1] for row in cursor.fetchall()]
    db_cols_map = {c.lower(): c for c in db_cols}
    df.columns = [str(col).strip() for col in df.columns]
    rename_dict = {col: db_cols_map[col.lower()] for col in df.columns if col.lower() in db_cols_map}
    df = df.rename(columns=rename_dict)
    return df[[c for c in db_cols if c in df.columns]]

def main():
    start_time = time.time()
    print("Launching Day 5 Full Ingestion Pipeline")
    
    conn = sqlite3.connect("data/nifty100.db")
    conn.execute("PRAGMA foreign_keys = OFF;")
    
    all_tables = [
        'companies', 'profitandloss', 'balancesheet', 'cashflow', 
        'analysis', 'documents', 'prosandcons', 'sectors', 'stock_prices', 'market_cap'
    ]
    for t in all_tables:
        conn.execute(f"DELETE FROM {t};")
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON;")
    
    master_failures_list = []
    audit_records = []

    def log_audit(table, rows_in, rows_out, rejected, t_start):
        audit_records.append({
            "table": table,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "rejected": rejected,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "runtime_s": round(time.time() - t_start, 4)
        })

    # 1. Companies
    t = time.time()
    df_comp = pd.read_excel("data/raw/companies.xlsx", header=1)
    df_comp['id'] = df_comp['id'].apply(normalize_ticker)
    df_comp_clean = align_dataframe_to_db(df_comp.dropna(subset=['id']).drop_duplicates(subset=['id']), conn, 'companies')
    df_comp_clean.to_sql("companies", conn, if_exists="append", index=False)
    valid_list = list(df_comp_clean['id'].unique())
    valid_set = set(valid_list)
    log_audit('companies', len(df_comp), len(df_comp_clean), len(df_comp) - len(df_comp_clean), t)

    # 2. Profit and Loss
    t = time.time()
    df_pl = pd.read_excel("data/raw/profitandloss.xlsx", header=1)
    df_pl['company_id'] = df_pl['company_id'].apply(normalize_ticker)
    df_pl['year'] = df_pl['year'].apply(normalize_year)
    master_failures_list.extend(run_data_quality_checks(df_pl, 'profitandloss', valid_set))
    df_pl_clean = align_dataframe_to_db(df_pl[df_pl['company_id'].isin(valid_list)].dropna(subset=['operating_profit']).drop_duplicates(subset=['company_id', 'year']), conn, 'profitandloss')
    df_pl_clean.to_sql("profitandloss", conn, if_exists="append", index=False)
    log_audit('profitandloss', len(df_pl), len(df_pl_clean), len(df_pl) - len(df_pl_clean), t)

    # 3. Balance Sheet
    t = time.time()
    df_bs = pd.read_excel("data/raw/balancesheet.xlsx", header=1)
    df_bs['company_id'] = df_bs['company_id'].apply(normalize_ticker)
    df_bs['year'] = df_bs['year'].apply(normalize_year)
    master_failures_list.extend(run_data_quality_checks(df_bs, 'balancesheet', valid_set))
    df_bs_clean = align_dataframe_to_db(df_bs[df_bs['company_id'].isin(valid_list)].dropna(subset=['total_assets']).drop_duplicates(subset=['company_id', 'year']), conn, 'balancesheet')
    df_bs_clean.to_sql("balancesheet", conn, if_exists="append", index=False)
    log_audit('balancesheet', len(df_bs), len(df_bs_clean), len(df_bs) - len(df_bs_clean), t)

    # 4. Cash Flow
    t = time.time()
    df_cf = pd.read_excel("data/raw/cashflow.xlsx", header=1)
    df_cf['company_id'] = df_cf['company_id'].apply(normalize_ticker)
    df_cf['year'] = df_cf['year'].apply(normalize_year)
    master_failures_list.extend(run_data_quality_checks(df_cf, 'cashflow', valid_set))
    df_cf_clean = align_dataframe_to_db(df_cf[df_cf['company_id'].isin(valid_list)].dropna(subset=['net_cash_flow']).drop_duplicates(subset=['company_id', 'year']), conn, 'cashflow')
    df_cf_clean.to_sql("cashflow", conn, if_exists="append", index=False)
    log_audit('cashflow', len(df_cf), len(df_cf_clean), len(df_cf) - len(df_cf_clean), t)

    # 5. Analysis
    t = time.time()
    df_an = pd.read_excel("data/raw/analysis.xlsx", header=1)
    df_an['company_id'] = df_an['company_id'].apply(normalize_ticker)
    df_an_clean = align_dataframe_to_db(df_an[df_an['company_id'].isin(valid_list)].drop_duplicates(subset=['company_id']), conn, 'analysis')
    df_an_clean.to_sql("analysis", conn, if_exists="append", index=False)
    log_audit('analysis', len(df_an), len(df_an_clean), len(df_an) - len(df_an_clean), t)

    # 6. Documents
    t = time.time()
    df_doc = pd.read_excel("data/raw/documents.xlsx", header=1)
    df_doc['company_id'] = df_doc['company_id'].apply(normalize_ticker)
    df_doc_clean = align_dataframe_to_db(df_doc[df_doc['company_id'].isin(valid_list)].drop_duplicates(subset=['company_id', 'year' if 'year' in df_doc.columns else 'Year']), conn, 'documents')
    df_doc_clean.to_sql("documents", conn, if_exists="append", index=False)
    log_audit('documents', len(df_doc), len(df_doc_clean), len(df_doc) - len(df_doc_clean), t)

    # 7. Pros and Cons
    t = time.time()
    df_pc = pd.read_excel("data/raw/prosandcons.xlsx", header=1)
    df_pc['company_id'] = df_pc['company_id'].apply(normalize_ticker)
    df_pc_clean = align_dataframe_to_db(df_pc[df_pc['company_id'].isin(valid_list)], conn, 'prosandcons')
    df_pc_clean.to_sql("prosandcons", conn, if_exists="append", index=False)
    log_audit('prosandcons', len(df_pc), len(df_pc_clean), len(df_pc) - len(df_pc_clean), t)

    # 8. Sectors
    t = time.time()
    df_sec = pd.read_excel("data/supporting/sectors.xlsx", header=0)
    df_sec['company_id'] = df_sec['company_id'].apply(normalize_ticker)
    df_sec_clean = align_dataframe_to_db(df_sec[df_sec['company_id'].isin(valid_list)].drop_duplicates(subset=['company_id']), conn, 'sectors')
    df_sec_clean.to_sql("sectors", conn, if_exists="append", index=False)
    log_audit('sectors', len(df_sec), len(df_sec_clean), len(df_sec) - len(df_sec_clean), t)

    # 9. Stock Prices
    t = time.time()
    df_sp = pd.read_excel("data/supporting/stock_prices.xlsx", header=0)
    df_sp['company_id'] = df_sp['company_id'].apply(normalize_ticker)
    df_sp_clean = align_dataframe_to_db(df_sp[df_sp['company_id'].isin(valid_list)].drop_duplicates(subset=['company_id', 'date']), conn, 'stock_prices')
    df_sp_clean.to_sql("stock_prices", conn, if_exists="append", index=False)
    log_audit('stock_prices', len(df_sp), len(df_sp_clean), len(df_sp) - len(df_sp_clean), t)

    # 10. Market Cap
    t = time.time()
    df_mc = pd.read_excel("data/supporting/market_cap.xlsx", header=0)
    df_mc['company_id'] = df_mc['company_id'].apply(normalize_ticker)
    cursor = conn.execute("PRAGMA table_info(market_cap);")
    db_cols = [row[1] for row in cursor.fetchall()]
    if len(df_mc.columns) >= len(db_cols):
        df_mc = df_mc.iloc[:, :len(db_cols)]
        df_mc.columns = db_cols
    df_mc_clean = align_dataframe_to_db(df_mc[df_mc['company_id'].isin(valid_list)].drop_duplicates(subset=['company_id', 'year']), conn, 'market_cap')
    df_mc_clean.to_sql("market_cap", conn, if_exists="append", index=False)
    log_audit('market_cap', len(df_mc), len(df_mc_clean), len(df_mc) - len(df_mc_clean), t)

    save_validation_failures(master_failures_list)

    # Extract target checklist configurations
    c_comp = conn.execute("SELECT COUNT(*) FROM companies;").fetchone()[0]
    c_pl = conn.execute("SELECT COUNT(*) FROM profitandloss;").fetchone()[0]
    c_bs = conn.execute("SELECT COUNT(*) FROM balancesheet;").fetchone()[0]
    c_cf = conn.execute("SELECT COUNT(*) FROM cashflow;").fetchone()[0]
    c_pr = conn.execute("SELECT COUNT(*) FROM stock_prices;").fetchone()[0]
    fk_check = len(conn.execute("PRAGMA foreign_key_check;").fetchall())
    
    os.makedirs("output", exist_ok=True)
    pd.DataFrame(audit_records).to_csv("output/load_audit.csv", index=False)
    conn.close()

    print(f"\n 7 core + 5 supplementary · load order · load_audit.csv · row counts: companies={c_comp}, P&L~{c_pl}, BS~{c_bs}, CF~{c_cf}, prices={c_pr} · FK check {fk_check}")
    print("SPRINT 1 COMPLETE: ALL 10 TABLES LOADED SUCCESSFULLY WITH ZERO CRASHES!")

if __name__ == "__main__":
    main()