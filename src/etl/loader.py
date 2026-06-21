import os
import sqlite3

def main():
    print("[*] Rebuilding a fresh database structure...")
    db_path = "data/nifty100.db"
    schema_path = "src/etl/schema.sql"
    
    os.makedirs("data", exist_ok=True)
    
    # Force delete old file if it exists to clean out sticky layouts
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            pass

    try:
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, "r") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
            print("[+] Blank database tables built successfully from schema.sql!")
    except sqlite3.Error as e:
        print(f"[-] Database build failed: {e}")

if __name__ == "__main__":
    main()