import sqlite3

def check_my_database():
    db_path = "data/nifty100.db"
    print(f"[*] Opening database to check tables...")
    
    # 1. Connect to our new database file
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. Ask SQLite for the names of all tables inside it
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    conn.close()
    
    # 3. Print out what we found
    print(f"\n[+] Found {len(tables)} tables inside the database:")
    for t in tables:
        print(f" -> {t[0]}")

if __name__ == "__main__":
    check_my_database()