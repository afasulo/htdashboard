import sqlite3
import pandas as pd
from config import HITTRAX_CONFIG

def get_db_connection():
    """Create a connection to the SQLite database"""
    return sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])

def get_hittrax_data():
    """Get all HitTrax data from SQLite database"""
    try:
        conn = get_db_connection()
        
        query = """
        SELECT 
            s.*,
            u.FirstName,
            u.LastName,
            u.FirstName || ' ' || u.LastName as Name,
            u.HeightFeet as Height,  -- Get converted height
            u.WeightLbs as Weight    -- Get converted weight
        FROM SessionConverted s  -- Use converted view
        LEFT JOIN UsersConverted u ON s.UserId = u.Id  -- Use converted view
        WHERE s.SkillLevel IS NOT NULL
        ORDER BY s.TimeStamp DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error querying SQLite database: {str(e)}")
        return pd.DataFrame()

def calculate_player_stats(df, min_ab=10):
    """Calculate player statistics from session data"""
    try:
        stats = df.groupby(['Name', 'SkillLevel']).agg({
            'AB': 'sum',
            'MaxExitVelMph': 'max',        # Using converted columns
            'AvgExitVelMph': 'mean',       # Using converted columns
            'MaxDistanceFeet': 'max',      # Using converted columns
            'AVG': 'mean',
            'SLG': 'mean',
            'HomeRuns': 'sum',
            'HitCount': 'sum'
        }).reset_index()
        
        # Filter for minimum at-bats
        stats = stats[stats['AB'] >= min_ab]
        
        return stats
        
    except Exception as e:
        print(f"Error calculating player stats: {str(e)}")
        return pd.DataFrame()

def get_player_details(player_name):
    """Get detailed session data for a specific player"""
    try:
        conn = get_db_connection()
        
        query = """
        SELECT 
            s.*,
            u.FirstName || ' ' || u.LastName as Name,
            u.School,
            u.HeightFeet as Height,    -- Get converted height
            u.WeightLbs as Weight      -- Get converted weight
        FROM SessionConverted s        -- Use converted view
        LEFT JOIN UsersConverted u ON s.UserId = u.Id  -- Use converted view
        WHERE u.FirstName || ' ' || u.LastName = ?
        ORDER BY s.TimeStamp DESC
        """
        
        df = pd.read_sql(query, conn, params=(player_name,))
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error getting player details: {str(e)}")
        return pd.DataFrame()

def get_available_skill_levels():
    """Get list of all skill levels in the database"""
    try:
        conn = get_db_connection()
        query = "SELECT DISTINCT SkillLevel FROM Session WHERE SkillLevel IS NOT NULL ORDER BY SkillLevel"
        df = pd.read_sql(query, conn)
        conn.close()
        return df['SkillLevel'].tolist()
    except Exception as e:
        print(f"Error getting skill levels: {str(e)}")
        return []

def get_available_players():
    """Get list of all players in the database"""
    try:
        conn = get_db_connection()
        query = """
        SELECT DISTINCT FirstName || ' ' || LastName as Name 
        FROM Users 
        ORDER BY Name
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df['Name'].tolist()
    except Exception as e:
        print(f"Error getting players: {str(e)}")
        return []