# leaderboard_debug.py
import sqlite3
import pandas as pd
from config import HITTRAX_CONFIG

def get_db_connection():
    """Create a connection to the SQLite database"""
    return sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])

def debug_leaderboard_query():
    """Debug the leaderboard query by checking each step"""
    try:
        print("Starting debug process...")
        print(f"Attempting to connect to database: {HITTRAX_CONFIG['sqlite_db']}")
        
        conn = get_db_connection()
        print("Database connection successful!")
        
        # Check if Users table exists
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables_df = pd.read_sql(tables_query, conn)
        print("\nAvailable tables in database:")
        print(tables_df)
        
        if 'Users' in tables_df['name'].values:
            # First check - Simple user count
            print("\nChecking Users table:")
            user_query = """
            SELECT 
                COUNT(*) as total_count,
                SUM(CASE WHEN GraduationYear IS NOT NULL THEN 1 ELSE 0 END) as grad_year_count
            FROM Users
            """
            user_df = pd.read_sql(user_query, conn)
            print(f"Total users: {user_df['total_count'].iloc[0]}")
            print(f"Users with graduation year: {user_df['grad_year_count'].iloc[0]}")
            
            # Check graduation year distribution
            print("\nChecking graduation year distribution:")
            grad_query = """
            SELECT 
                GraduationYear,
                COUNT(*) as count 
            FROM Users 
            WHERE GraduationYear IS NOT NULL
            GROUP BY GraduationYear 
            ORDER BY GraduationYear
            """
            grad_df = pd.read_sql(grad_query, conn)
            print(grad_df)
            
            # Sample some user records
            print("\nSample user records:")
            sample_query = """
            SELECT 
                FirstName || ' ' || LastName as Name,
                GraduationYear,
                BirthDate,
                School
            FROM Users
            LIMIT 5
            """
            sample_df = pd.read_sql(sample_query, conn)
            print(sample_df)
            
            # Check UsersConverted view
            print("\nChecking if UsersConverted view exists:")
            views_query = "SELECT name FROM sqlite_master WHERE type='view'"
            views_df = pd.read_sql(views_query, conn)
            print("Available views:")
            print(views_df)
            
            if 'UsersConverted' in views_df['name'].values:
                print("\nSample from UsersConverted view:")
                converted_query = "SELECT * FROM UsersConverted LIMIT 5"
                converted_df = pd.read_sql(converted_query, conn)
                print(converted_df)
            else:
                print("WARNING: UsersConverted view does not exist!")
                
            # Check Session data
            print("\nChecking Session data:")
            session_query = "SELECT COUNT(*) as count FROM Session"
            session_df = pd.read_sql(session_query, conn)
            print(f"Total sessions: {session_df['count'].iloc[0]}")
            
        else:
            print("WARNING: Users table not found in database!")
            
        conn.close()
        print("\nDebug process complete!")
        
    except Exception as e:
        print(f"\nError during debug process: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting leaderboard diagnostics...")
    debug_leaderboard_query()