import sqlite3
import pymssql
from config import HITTRAX_CONFIG
import os

def debug_sync():
    print("=== Database Sync Debug ===")
    
    # 1. Check SQLite database permissions and existence
    sqlite_path = HITTRAX_CONFIG['sqlite_db']
    print(f"\nChecking SQLite database at: {os.path.abspath(sqlite_path)}")
    
    if os.path.exists(sqlite_path):
        print(f"Database exists, size: {os.path.getsize(sqlite_path)} bytes")
        print(f"File permissions: {oct(os.stat(sqlite_path).st_mode)[-3:]}")
        try:
            # Try opening for writing
            with open(sqlite_path, 'ab') as f:
                print("File is writable")
        except PermissionError:
            print("WARNING: File is not writable!")
    else:
        print("WARNING: SQLite database file not found!")

    # 2. Compare source and destination data
    try:
        print("\nConnecting to source SQL Server...")
        source_conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
        source_cursor = source_conn.cursor()
        
        print("\nConnecting to SQLite...")
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Check a few random users
        source_cursor.execute("""
            SELECT TOP 5 Id, FirstName, LastName, GraduationYear 
            FROM Users 
            ORDER BY NEWID()
        """)
        source_users = source_cursor.fetchall()
        
        print("\nComparing sample user data:")
        print("\nSource database (SQL Server):")
        for user in source_users:
            print(f"ID: {user[0]}, Name: {user[1]} {user[2]}, Grad Year: {user[3]}")
            
            # Check corresponding SQLite record
            sqlite_cursor.execute("""
                SELECT FirstName, LastName, GraduationYear 
                FROM Users 
                WHERE Id = ?
            """, (user[0],))
            sqlite_user = sqlite_cursor.fetchone()
            
            print("SQLite database:")
            if sqlite_user:
                print(f"ID: {user[0]}, Name: {sqlite_user[0]} {sqlite_user[1]}, Grad Year: {sqlite_user[2]}")
                if user[3] != sqlite_user[2]:
                    print(">>> MISMATCH DETECTED <<<")
            else:
                print(f"User ID {user[0]} not found in SQLite database!")
            print("-" * 50)
        
        source_conn.close()
        sqlite_conn.close()
        
    except Exception as e:
        print(f"\nError during debug: {str(e)}")

if __name__ == "__main__":
    debug_sync()