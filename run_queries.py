import sqlite3
import pandas as pd

conn=sqlite3.connect("db/n100.sqlite")

query = """
SELECT DISTINCT company_id
FROM balancesheet

EXCEPT

SELECT DISTINCT company_id
FROM profitandloss;
"""

df=pd.read_sql(query,conn)
print(df)
conn.close()