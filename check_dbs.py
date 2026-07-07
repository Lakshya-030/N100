import sqlite3
import pandas as pd
import os

def check_db(db_path):
    if not os.path.exists(db_path):
        print(f"\n[⚠️ NOT FOUND] File nahi mili: {db_path}")
        return
        
    print(f"\n🔎 Checking: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables check karte hain
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"  Available Tables: {tables}")
    
    # Market Cap table rows check karte hain
    if 'market_cap' in tables:
        df = pd.read_sql_query("SELECT COUNT(*) as cnt FROM market_cap;", conn)
        print(f"  market_cap Rows Count: {df['cnt'].iloc[0]}")
    else:
        print("  market_cap table is MISSING in this DB!")
        
    conn.close()

if __name__ == "__main__":
    check_db(os.path.join("data", "nifty100.db"))
    check_db("financials.db")