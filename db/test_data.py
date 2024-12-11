# test_data.py
import sqlite3
import pandas as pd

def check_data():
    """Check the contents of the local database"""
    conn = sqlite3.connect('hittrax_local.db')
    
    print("\nChecking database contents:")
    print("-" * 50)
    
    # Check Users
    df_users = pd.read_sql("SELECT * FROM Users LIMIT 5", conn)
    print(f"\nUsers count: {len(pd.read_sql('SELECT * FROM Users', conn))}")
    print("\nSample Users:")
    print(df_users[['FirstName', 'LastName', 'SkillLevel']].head())
    
    # Check Sessions
    df_sessions = pd.read_sql("SELECT * FROM Session LIMIT 5", conn)
    print(f"\nSessions count: {len(pd.read_sql('SELECT * FROM Session', conn))}")
    print("\nSample Sessions (with converted units):")
    print(df_sessions[['MaxExitVel', 'MaxDistance', 'HitCount']].head())
    
    # Check Plays
    df_plays = pd.read_sql("SELECT * FROM Plays LIMIT 5", conn)
    print(f"\nPlays count: {len(pd.read_sql('SELECT * FROM Plays', conn))}")
    print("\nSample Plays (with converted units):")
    print(df_plays[['ExitVelo', 'Distance', 'PitchVel']].head())
    
    conn.close()

if __name__ == "__main__":
    check_data()