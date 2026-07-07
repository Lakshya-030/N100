import sqlite3
import pandas as pd
import yaml
import os

def load_screener_config():
    config_path = os.path.join("config", "screener_config.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def get_latest_screener_data(conn):
    """
    PROFESSIONAL APPROACH: No fake averages or IFNULL overrides.
    Strictly type-cast the join vectors to resolve any implicit data type mismatches.
    """
    query = """
    SELECT 
        fr.company_id,
        CAST(fr.year AS INTEGER) as year,
        fr.net_profit_margin_pct,
        fr.operating_profit_margin_pct,
        fr.return_on_equity_pct,
        fr.debt_to_equity,
        fr.interest_coverage,
        fr.asset_turnover,
        fr.free_cash_flow_cr,
        fr.dividend_payout_ratio_pct,
        fr.revenue_cagr_5yr,
        fr.pat_cagr_5yr,
        fr.eps_cagr_5yr,
        fr.composite_quality_score,
        pl.sales,
        mc.pe_ratio,
        mc.pb_ratio,
        mc.dividend_yield_pct,
        -- Renaming broad_sector as peer_group for clean ranking abstraction
        s.broad_sector as peer_group
    FROM financial_ratios fr
    LEFT JOIN market_cap mc ON fr.company_id = mc.company_id AND CAST(fr.year AS INTEGER) = CAST(mc.year AS INTEGER)
    LEFT JOIN profitandloss pl ON fr.company_id = pl.company_id AND CAST(fr.year AS INTEGER) = CAST(pl.year AS INTEGER)
    LEFT JOIN sectors s ON fr.company_id = s.company_id
    WHERE CAST(fr.year AS INTEGER) = (SELECT MAX(CAST(year AS INTEGER)) FROM financial_ratios);
    """
    return pd.read_sql_query(query, conn)

def compute_peer_percentiles(df):
    """
    DAY 17: Compute percentile rankings for all companies 
    within their respective peer groups (sectors) across 10 core metrics.
    """
    print("\n--- Day 17: Computing Peer Percentile Rankings (10 Metrics) ---")
    
    ranking_metrics = [
        'return_on_equity_pct', 'debt_to_equity', 'free_cash_flow_cr', 
        'pe_ratio', 'pb_ratio', 'dividend_yield_pct', 'interest_coverage', 
        'operating_profit_margin_pct', 'pat_cagr_5yr', 'sales'
    ]
    
    ranked_df = df.copy()
    
    for metric in ranking_metrics:
        if metric in ranked_df.columns:
            # Metrics where a lower value is better (e.g., P/E, P/B, Debt to Equity)
            ascending_order = True if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity'] else False
            
            # Using basic pandas group rank method with min strategy
            ranked_df[f'{metric}_percentile'] = (
                ranked_df.groupby('peer_group')[metric]
                .rank(pct=True, ascending=ascending_order, method='min') * 100
            )
            # Safe fillna for edge cases
            ranked_df[f'{metric}_percentile'] = ranked_df[f'{metric}_percentile'].fillna(0)
            
    return ranked_df

def apply_core_filters(df, rules, name=""):
    filtered_df = df.copy()
    
    # 1. Profitability Matrix
    if "min_roe" in rules:
        filtered_df = filtered_df[filtered_df["return_on_equity_pct"] >= rules["min_roe"]]
    if "min_npm" in rules:
        filtered_df = filtered_df[filtered_df["net_profit_margin_pct"] >= rules["min_npm"]]

    # 2. Leverage with Financials Carve-out
    if "max_de" in rules:
        is_financial = filtered_df["peer_group"].dropna().str.upper() == "FINANCIALS"
        passes_de = filtered_df["debt_to_equity"].notna() & (filtered_df["debt_to_equity"] <= rules["max_de"])
        filtered_df = filtered_df[is_financial | passes_de]

    # 3. Liquidity & Size
    if "min_fcf" in rules:
        filtered_df = filtered_df[filtered_df["free_cash_flow_cr"] >= rules["min_fcf"]]
    if "min_sales" in rules:
        filtered_df = filtered_df[filtered_df["sales"] >= rules["min_sales"]]

    # 4. Valuation Vector Parameters
    if "max_pe" in rules:
        filtered_df = filtered_df[filtered_df["pe_ratio"].notna() & (filtered_df["pe_ratio"] <= rules["max_pe"])]
    if "max_pb" in rules:
        filtered_df = filtered_df[filtered_df["pb_ratio"].notna() & (filtered_df["pb_ratio"] <= rules["max_pb"])]
    if "min_div_yield" in rules:
        filtered_df = filtered_df[filtered_df["dividend_yield_pct"].notna() & (filtered_df["dividend_yield_pct"] >= rules["min_div_yield"])]
    if "max_div_payout" in rules:
        filtered_df = filtered_df[filtered_df["dividend_payout_ratio_pct"].notna() & (filtered_df["dividend_payout_ratio_pct"] <= rules["max_div_payout"])]

    # 5. Long-term Growth
    if "min_revenue_cagr_5yr" in rules:
        filtered_df = filtered_df[filtered_df["revenue_cagr_5yr"] >= rules["min_revenue_cagr_5yr"]]

    if "composite_quality_score" in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by="composite_quality_score", ascending=False)
        
    return filtered_df

def execute_screener_pipeline():
    db_path = os.path.join("data", "nifty100.db")
    conn = sqlite3.connect(db_path)
    
    base_df = get_latest_screener_data(conn)
    config = load_screener_config()
    presets = config.get("presets", {})
    
    # [DAY 17] Process data-layer with percentile analytics
    processed_df = compute_peer_percentiles(base_df)
    
    print("\n--- Day 16 Strict Code Verification Run (Tuned) ---")
    screened_presets_dict = {}
    
    for name, rules in presets.items():
        res = apply_core_filters(processed_df, rules, name=name)
        screened_presets_dict[name] = res
        print(f"Preset Target Framework '{name}': Found {len(res)} true matching companies.")
        
    # [DAY 18] Generate Final Excel Deliverables
    print("\n--- Day 18: Generating Excel Deliverable Reports ---")
    os.makedirs("output", exist_ok=True)
    
    # 1. Multi-tab screener_output.xlsx
    screener_out_path = os.path.join("output", "screener_output.xlsx")
    with pd.ExcelWriter(screener_out_path, engine='openpyxl') as writer:
        for preset_name, preset_df in screened_presets_dict.items():
            preset_df.to_excel(writer, sheet_name=preset_name[:30], index=False)
    print(f"[SUCCESS] Generated multi-tab screener output sheet at: {screener_out_path}")
    
    # 2. Global peer_comparison.xlsx
    peer_out_path = os.path.join("output", "peer_comparison.xlsx")
    processed_df.to_excel(peer_out_path, sheet_name="Peer Rankings Master", index=False)
    print(f"[SUCCESS] Generated benchmark peer comparison matrix at: {peer_out_path}")
    
    conn.close()

if __name__ == "__main__":
    db_path = os.path.join("data", "nifty100.db")
    conn = sqlite3.connect(db_path)
    
    # 🔎 LIVE DIAGNOSTIC: Check if market_cap table has any non-null rows at all
    check_df = pd.read_sql_query("SELECT * FROM market_cap LIMIT 5;", conn)
    print("\n--- Market Cap Table Sample Data ---")
    print(check_df)
    
    # Check what columns are present in market_cap
    print("\n--- Market Cap Table Schema ---")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(market_cap);")
    print(cursor.fetchall())
    
    conn.close()
    
    # Run the pipeline components
    execute_screener_pipeline()