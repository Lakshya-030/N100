import sqlite3
import os

db_path = os.path.join("data", "nifty100.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]

print("\n=== Database Ke Andar Ke Saare Tables ===")
print(tables)


if "company_growth_metrics" in tables:
    print("\n[SUCCESS] 'company_growth_metrics' table database mein ban chuka hai!")
else:
    print("\n[ERROR] Table nahi mila.")

conn.close()