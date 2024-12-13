import sqlite3
import pandas as pd
import numpy as np
from config import HITTRAX_CONFIG

# Define column groups for the UI first
COLUMN_GROUPS = {
    'Basic Info': ['Name', 'UserId', 'SkillLevel'],
    'Velocity Stats (mph)': ['MaxPitchVelMph', 'MaxExitVelMph', 'AvgPitchVelMph', 'AvgExitVelMph', 'HHVelMph'],
    'Distance Stats (ft)': ['AvgDistanceFeet', 'MaxDistanceFeet', 'MaxGroundDistFeet', 'AvgGroundDistFeet'],
    'Hit Stats': ['Singles', 'Doubles', 'Triples', 'HomeRuns', 'FoulBalls', 'HitCount', 'HHCount', 'AB'],
    'Pitch Stats': ['PitchCount', 'Strikes', 'Balls'],
    'Percentages': ['AVG', 'SLG', 'LDPercentage', 'FBPercentage', 'GBPercentage',
                   'LIPercentage', 'RIPercentage', 'CIPercentage', 'LOPercentage',
                   'ROPercentage', 'COPercentage'],
    'Scoring/Ranking': ['Score', 'MaxPoints', 'RankMaxVel', 'RankAvgVel', 'RankMaxDist', 'RankPoints']
}

# Define tooltips for each column type
COLUMN_TOOLTIPS = {
    'best': '🏆 Best value from all sessions',
    'average': '📊 Average across all sessions',
    'total': '📈 Total sum of all sessions',
    'weighted_avg': '⚖️ Weighted average based on attempts'
}

# Update column formats with tooltip information
COLUMN_FORMATS = {
    'best': {
        'columns': ['MaxExitVelMph', 'MaxPitchVelMph', 'MaxDistanceFeet', 'MaxGroundDistFeet', 'HHVelMph', 'MaxPoints'],
        'tooltip': COLUMN_TOOLTIPS['best']
    },
    'average': {
        'columns': ['AvgDistanceFeet', 'AvgGroundDistFeet', 'LDPercentage', 'FBPercentage', 
                   'GBPercentage', 'LOPercentage'],
        'tooltip': COLUMN_TOOLTIPS['average']
    },
    'total': {
        'columns': ['Singles', 'Doubles', 'Triples', 'HomeRuns', 'HitCount', 'AB', 'FoulBalls',
                   'HHCount', 'PitchCount', 'Strikes', 'Balls', 'Score'],
        'tooltip': COLUMN_TOOLTIPS['total']
    },
    'weighted_avg': {
        'columns': ['AVG', 'SLG', 'AvgExitVelMph', 'AvgPitchVelMph'],
        'tooltip': COLUMN_TOOLTIPS['weighted_avg']
    }
}

def get_db_connection():
    """Create a connection to the SQLite database"""
    try:
        conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
        print(f"Database connection type: {type(conn)}")  # Debug print
        print(f"Database path: {HITTRAX_CONFIG['sqlite_db']}")  # Debug print
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

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
            u.School,
            u.HeightFeet as Height,
            u.WeightLbs as Weight
        FROM SessionConverted s
        LEFT JOIN UsersConverted u ON s.UserId = u.Id
        WHERE s.SkillLevel IS NOT NULL
        ORDER BY s.TimeStamp DESC
        """
        
        df = pd.read_sql(query, conn)
        print(f"Retrieved {len(df)} rows from database")  # Debug print
        conn.close()
        
        return df
        
    except Exception as e:
        print(f"Error querying SQLite database: {str(e)}")
        return pd.DataFrame()

def calculate_player_stats(df, min_ab=10):
    """Calculate player statistics from session data"""
    try:
        if df.empty:
            return pd.DataFrame()
            
        # Group by player
        stats = df.groupby(['Name', 'SkillLevel']).agg({
            'AB': 'sum',
            'MaxExitVelMph': 'max',
            'AvgExitVelMph': 'mean',
            'MaxDistanceFeet': 'max',
            'AVG': 'mean',
            'SLG': 'mean',
            'HomeRuns': 'sum',
            'HitCount': 'sum'
        }).reset_index()
        
        # Filter for minimum at-bats
        stats = stats[stats['AB'] >= min_ab]
        print(f"Calculated stats for {len(stats)} players with {min_ab}+ at-bats")  # Debug print
        
        return stats
        
    except Exception as e:
        print(f"Error calculating player stats: {str(e)}")
        return pd.DataFrame()