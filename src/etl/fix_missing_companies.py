import sqlite3

conn = sqlite3.connect("db/n100.sqlite")
cur = conn.cursor()

missing = [
    "AGTL",
    "ULTRACEMCO",
    "UNIONBANK",
    "UNITDSPR",
    "VBL",
    "VEDL",
    "WIPRO",
    "ZOMATO",
    "ZYDUSLIFE"
]

for ticker in missing:
    cur.execute(
        """
        INSERT OR IGNORE INTO companies
        (id, company_name)
        VALUES (?, ?)
        """,
        (ticker, ticker)
    )

conn.commit()
conn.close()

print("Missing companies added")
