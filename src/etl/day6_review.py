import sqlite3
import pandas as pd

def main():
    print("=== Day 06: Data Quality Manual Review ===")
    conn = sqlite3.connect("data/nifty100.db")
    
    # This connects the companies and sectors tables together using basic SQL
    query = """
    SELECT c.id, c.company_name, s.broad_sector 
    FROM companies c 
    JOIN sectors s ON c.id = s.company_id 
    ORDER BY RANDOM() 
    LIMIT 5;
    """
    
    # 1. Grab the 5 random companies
    sample_companies = pd.read_sql(query, conn)
    print("\n[+] Step 1: Selected 5 Random Companies for Audit:")
    print(sample_companies.to_string(index=False))
    print("-" * 60)

    # 2. Check how many years of data they have
    print("[+] Step 2: Running Time-Series Coverage and Inventory Profiles:")
    for _, row in sample_companies.iterrows():
        ticker = row['id']
        name = row['company_name']
        
        pl_count = conn.execute("SELECT COUNT(*) FROM profitandloss WHERE company_id = ?;", (ticker,)).fetchone()[0]
        bs_count = conn.execute("SELECT COUNT(*) FROM balancesheet WHERE company_id = ?;", (ticker,)).fetchone()[0]
        cf_count = conn.execute("SELECT COUNT(*) FROM cashflow WHERE company_id = ?;", (ticker,)).fetchone()[0]
        
        print(f"\n• Company: {ticker} ({name})")
        print(f"  - Profit & Loss Rows : {pl_count}")
        print(f"  - Balance Sheet Rows : {bs_count}")
        print(f"  - Cash Flow Rows    : {cf_count}")
        
        # Alert if data history is too short
        if pl_count < 5 or bs_count < 5 or cf_count < 5:
            print(f"  ⚠️  [WARNING] Less than 5 years of data found.")
        else:
            print(f"  ✔ Good amount of data history confirmed.")

    print("-" * 60)
    
    # 3. Double-check final assignment rules
    print("[+] Step 3: Verifying Final Rules:")
    tot_companies = conn.execute("SELECT COUNT(*) FROM companies;").fetchone()[0]
    fk_violations = len(conn.execute("PRAGMA foreign_key_check;").fetchall())
    
    print(f"  ✔ Total companies in database = {tot_companies} (Goal: 92)")
    print(f"  ✔ Broken database links (FK violations) = {fk_violations} (Goal: 0)")
    
    if tot_companies == 92 and fk_violations == 0:
        print("\n[++++] ALL CHECKS PASS: DAY 6 MANUAL REVIEW COMPLETED SUCCESSFULLY! [++++]")
    else:
        print("\n[-] Something is missing. Re-run your load_all.py file.")
        
    conn.close()

if __name__ == "__main__":
    main()