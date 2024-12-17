# db_utils.py
import sqlite3
import pandas as pd
from config import HITTRAX_CONFIG

# Column grouping definitions
COLUMN_GROUPS = {
    'Basic Info': ['Name', 'UserId', 'GraduationYear'],
    'Velocity Stats (mph)': ['MaxPitchVelMph', 'MaxExitVelMph', 'AvgPitchVelMph', 'AvgExitVelMph', 'HHVelMph'],
    'Distance Stats (ft)': ['AvgDistanceFeet', 'MaxDistanceFeet', 'MaxGroundDistFeet', 'AvgGroundDistFeet'],
    'Hit Stats': ['Singles', 'Doubles', 'Triples', 'HomeRuns', 'FoulBalls', 'HitCount', 'HHCount', 'AB'],
    'Pitch Stats': ['PitchCount', 'Strikes', 'Balls'],
    'Percentages': ['AVG', 'SLG', 'LDPercentage', 'FBPercentage', 'GBPercentage',
                   'LIPercentage', 'RIPercentage', 'CIPercentage', 'LOPercentage',
                   'ROPercentage', 'COPercentage'],
    'Scoring/Ranking': ['Score', 'MaxPoints', 'RankMaxVel', 'RankAvgVel', 'RankMaxDist', 'RankPoints']
}

# Column tooltips
COLUMN_TOOLTIPS = {
    'best': '🏆 Best value from all sessions',
    'average': '📊 Average across all sessions',
    'total': '📈 Total sum of all sessions',
    'weighted_avg': '⚖️ Weighted average based on attempts'
}

# Column formatting configurations
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


class DatabaseManager:
    """Centralized database management class"""
    
    @staticmethod
    def get_connection():
        """Create a connection to the SQLite database"""
        try:
            conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
            return conn
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    @staticmethod
    def get_hittrax_data():
        """Get all HitTrax data from SQLite database"""
        try:
            conn = DatabaseManager.get_connection()
            
            query = """
            SELECT 
                s.*,
                u.FirstName,
                u.LastName,
                u.FirstName || ' ' || u.LastName as Name,
                u.School,
                u.HeightFeet as Height,
                u.WeightLbs as Weight,
                u.GraduationYear
            FROM SessionConverted s
            LEFT JOIN UsersConverted u ON s.UserId = u.Id
            WHERE s.Active = 1
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            return df
            
        except Exception as e:
            print(f"Error querying SQLite database: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def calculate_player_stats(df, min_ab=10):
        """Calculate player statistics from session data"""
        try:
            if df.empty:
                return pd.DataFrame()
                
            stats = df.groupby(['Name', 'GraduationYear']).agg({
                'AB': 'sum',
                'MaxExitVelMph': 'max',
                'AvgExitVelMph': 'mean',
                'MaxDistanceFeet': 'max',
                'AVG': 'mean',
                'SLG': 'mean',
                'HomeRuns': 'sum',
                'HitCount': 'sum'
            }).reset_index()
            
            stats = stats[stats['AB'] >= min_ab]
            return stats
            
        except Exception as e:
            print(f"Error calculating player stats: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def get_player_details(player_name):
        """Get detailed session data for a specific player"""
        try:
            conn = DatabaseManager.get_connection()
            
            query = """
            SELECT 
                s.*,
                u.FirstName || ' ' || u.LastName as Name,
                u.School,
                u.HeightFeet as Height,
                u.WeightLbs as Weight
            FROM SessionConverted s
            LEFT JOIN UsersConverted u ON s.UserId = u.Id
            WHERE u.FirstName || ' ' || u.LastName = ?
            ORDER BY s.TimeStamp DESC
            """
            
            df = pd.read_sql(query, conn, params=(player_name,))
            conn.close()
            return df
            
        except Exception as e:
            print(f"Error getting player details: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def verify_database():
        """Verify database integrity and contents"""
        print("\n=== Database Verification ===")
        try:
            conn = DatabaseManager.get_connection()
            
            # Check tables
            tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
            print(f"\nTables found: {', '.join(tables['name'])}")
            
            # Check views
            views = pd.read_sql("SELECT name FROM sqlite_master WHERE type='view'", conn)
            print(f"\nViews found: {', '.join(views['name'])}")
            
            # Sample data counts
            tables_to_check = ['Users', 'Session', 'Plays']
            for table in tables_to_check:
                count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn)['count'][0]
                print(f"\n{table} count: {count:,}")
            
            conn.close()
            print("\n=== Verification Complete ===")
            
        except Exception as e:
            print(f"Error during verification: {str(e)}")