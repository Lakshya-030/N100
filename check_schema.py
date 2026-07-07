import sqlite3

conn = sqlite3.connect("data/nifty100.db")
cursor = conn.cursor()

# Saari tables ke naam aur unke exact columns nikalne ke liye query
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("--- ACTUAL DATABASE SCHEMA ---")
for table in tables:
    t_name = table[0]
    print(f"\nTable: {t_name}")
    cursor.execute(f"PRAGMA table_info({t_name});")
    cols = cursor.fetchall()
    for col in cols:
        print(f"  - Column ID: {col[0]} | Name: '{col[1]}' | Type: {col[2]}")

conn.close()