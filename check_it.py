import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")
df = pd.read_sql_query("SELECT company_id, year, peer_group, return_on_equity_pct FROM financial_ratios WHERE peer_group='IT Services'", conn)
conn.close()

print(df.to_string())