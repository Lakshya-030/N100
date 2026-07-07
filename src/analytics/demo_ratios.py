import sqlite3
import pandas as pd
import os

def show_table_demo():
    print("--- Day 14: Financial Ratios Table Handoff Demo (FY2024 Corrected) ---")
    db_path = os.path.join("data", "nifty100.db")
    conn = sqlite3.connect(db_path)
    
    # 🌟 CRITICAL FIX: Fetch entries strictly for the latest operational year (2024)
    # to ensure 5-Year historical CAGR vectors have matured and are populated.
    query = """
    SELECT * FROM financial_ratios 
    WHERE year = (SELECT MAX(year) FROM financial_ratios)
    ORDER BY company_id ASC 
    LIMIT 5;
    """
    df = pd.read_sql_query(query, conn)
    
    if df.empty:
        # Fallback if specific exact max year filter constraints require soft limits
        query = """
        SELECT * FROM financial_ratios 
        WHERE year = 2024
        ORDER BY company_id ASC 
        LIMIT 5;
        """
        df = pd.read_sql_query(query, conn)
        
    for idx, row in df.iterrows():
        print("\n" + "="*60)
        print(f" COMPANY: {row['company_id']} | YEAR: {row['year']} ")
        print("="*60)
        print(f"  1. Net Profit Margin        : {row['net_profit_margin_pct']}%")
        print(f"  2. Operating Profit Margin  : {row['operating_profit_margin_pct']}%")
        print(f"  3. Return on Equity (ROE)   : {row['return_on_equity_pct']}%")
        print(f"  4. Debt to Equity (D/E)     : {row['debt_to_equity']}")
        print(f"  5. Interest Coverage Ratio  : {row['interest_coverage']}")
        print(f"  6. Asset Turnover           : {row['asset_turnover']}x")
        print(f"  7. Free Cash Flow (Cr)      : {row['free_cash_flow_cr']} Cr")
        print(f"  8. CapEx (Cr)               : {row['capex_cr']} Cr")
        print(f"  9. Earnings Per Share (EPS) : ₹{row['earnings_per_share']}")
        print(f" 10. Book Value Per Share     : ₹{row['book_value_per_share']}")
        print(f" 11. Dividend Payout Ratio    : {row['dividend_payout_ratio_pct']}%")
        print(f" 12. Total Debt (Cr)          : {row['total_debt_cr']} Cr")
        print(f" 13. Cash from Operations (Cr): {row['cash_from_operations_cr']} Cr")
        print(f" 14. 5-Year Revenue CAGR      : {row['revenue_cagr_5yr']}%")
        print(f" 15. 5-Year PAT CAGR          : {row['pat_cagr_5yr']}%")
        print(f" 16. 5-Year EPS CAGR          : {row['eps_cagr_5yr']}%")
        print("-" * 60)
        print(f" 🌟 COMPOSITE QUALITY SCORE   : {row['composite_quality_score']} / 10")
        print("="*60)

    conn.close()

if __name__ == "__main__":
    show_table_demo()