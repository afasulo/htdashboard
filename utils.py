import pymssql
import pandas as pd
import numpy as np

# Define column groups for the UI first
COLUMN_GROUPS = {
    'Basic Info': ['Name', 'UserId', 'SkillLevel'],
    'Velocity Stats (mph)': ['MaxPitchVel', 'MaxExitVel', 'AvgPitchVel', 'AvgExitVel', 'HHVel'],
    'Distance Stats (m)': ['AvgDistance', 'AvgElevation', 'MaxDistance', 'MaxGroundDist', 'AvgGroundDist'],
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
        'columns': ['MaxExitVel', 'MaxPitchVel', 'MaxDistance', 'MaxGroundDist', 'HHVel', 'MaxPoints'],
        'tooltip': COLUMN_TOOLTIPS['best']
    },
    'average': {
        'columns': ['AvgDistance', 'AvgElevation', 'AvgGroundDist', 'LDPercentage', 'FBPercentage', 
                   'GBPercentage', 'LOPercentage'],
        'tooltip': COLUMN_TOOLTIPS['average']
    },
    'total': {
        'columns': ['Singles', 'Doubles', 'Triples', 'HomeRuns', 'HitCount', 'AB', 'FoulBalls',
                   'HHCount', 'PitchCount', 'Strikes', 'Balls', 'Score'],
        'tooltip': COLUMN_TOOLTIPS['total']
    },
    'weighted_avg': {
        'columns': ['AVG', 'SLG', 'AvgExitVel', 'AvgPitchVel'],
        'tooltip': COLUMN_TOOLTIPS['weighted_avg']
    }
}

def get_hittrax_data():
    try:
        settings = {
            'server': '192.168.113.172',
            'port': 1337,
            'database': 'HitTrax',
            'user': r'DESKTOP-TLAIKQ6\HitTraxPC',
            'password': 'baseball',
            'tds_version': '7.0',
            'charset': 'UTF-8'
        }
        
        conn = pymssql.connect(**settings)
        
        query = """
        SELECT 
            s.UserId,
            s.TimeStamp,
            u.Id AS UserId,
            s.MaxPitchVel,
            s.MaxExitVel,
            s.AvgPitchVel,
            s.AvgExitVel,
            s.AvgDistance,
            s.AvgElevation,
            s.MaxDistance,
            s.PitchCount,
            s.HitCount,
            s.Singles,
            s.Triples,
            s.Doubles,
            s.HomeRuns,
            s.FoulBalls,
            s.Strikes,
            s.Balls,
            s.SLG,
            s.AVG,
            s.LDPercentage,
            s.FBPercentage,
            s.GBPercentage,
            s.LIPercentage,
            s.RIPercentage,
            s.CIPercentage,
            s.LOPercentage,
            s.ROPercentage,
            s.COPercentage,
            s.HHCount,
            s.HHVel,
            s.MaxGroundDist,
            s.AvgGroundDist,
            s.Score,
            s.MaxPoints,
            s.AB,
            s.RankMaxVel,
            s.RankAvgVel,
            s.RankMaxDist,
            s.RankPoints,
            s.SkillLevel,
            u.FirstName,
            u.LastName
        FROM Session s
        LEFT JOIN Users u ON s.UserId = u.Id
        WHERE s.SkillLevel IS NOT NULL
        ORDER BY s.TimeStamp DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Convert velocity columns from m/s to mph
        velocity_columns = ['MaxPitchVel', 'MaxExitVel', 'AvgPitchVel', 'AvgExitVel', 'HHVel']
        for col in velocity_columns:
            df[col] = df[col].apply(lambda x: x * 2.237 if pd.notnull(x) else x)
            
        # Convert distance columns from feet to meters
        distance_columns = ['AvgDistance', 'AvgElevation', 'MaxDistance', 'MaxGroundDist', 'AvgGroundDist']
        for col in distance_columns:
            df[col] = df[col].apply(lambda x: x * 0.3048 if pd.notnull(x) else x)
            
        # Format percentage columns
        percentage_columns = ['AVG', 'SLG', 'LDPercentage', 'FBPercentage', 'GBPercentage',
                            'LIPercentage', 'RIPercentage', 'CIPercentage', 'LOPercentage',
                            'ROPercentage', 'COPercentage']
        for col in percentage_columns:
            df[col] = df[col].apply(lambda x: x/100 if pd.notnull(x) else x)
        
        # Create full name column
        df['Name'] = df['FirstName'].str.strip() + ' ' + df['LastName'].str.strip()
        df['Name'] = df['Name'].str.strip()
        
        return df
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return pd.DataFrame()

def calculate_player_summary(df):
    """Calculate summary statistics for each player."""
    try:
        if df.empty:
            return pd.DataFrame()
            
        # Group by player
        summary = df.groupby(['Name', 'SkillLevel']).agg({
            # Best (Maximum) values
            'MaxExitVel': 'max',
            'MaxPitchVel': 'max',
            'MaxDistance': 'max',
            'MaxGroundDist': 'max',
            'HHVel': 'max',
            'MaxPoints': 'max',
            
            # Simple averages
            'AvgDistance': 'mean',
            'AvgElevation': 'mean',
            'AvgGroundDist': 'mean',
            'LDPercentage': 'mean',
            'FBPercentage': 'mean',
            'GBPercentage': 'mean',
            'LOPercentage': 'mean',
            
            # Totals
            'Singles': 'sum',
            'Doubles': 'sum',
            'Triples': 'sum',
            'HomeRuns': 'sum',
            'HitCount': 'sum',
            'AB': 'sum',
            'FoulBalls': 'sum',
            'HHCount': 'sum',
            'PitchCount': 'sum',
            'Strikes': 'sum',
            'Balls': 'sum',
            'Score': 'sum'
        }).reset_index()
        
        # Calculate weighted averages separately to handle zero weights
        for player in summary['Name'].unique():
            player_data = df[df['Name'] == player]
            
            # Calculate AVG and SLG if AB > 0
            if player_data['AB'].sum() > 0:
                summary.loc[summary['Name'] == player, 'AVG'] = (
                    (player_data['AVG'] * player_data['AB']).sum() / player_data['AB'].sum()
                )
                summary.loc[summary['Name'] == player, 'SLG'] = (
                    (player_data['SLG'] * player_data['AB']).sum() / player_data['AB'].sum()
                )
            else:
                summary.loc[summary['Name'] == player, 'AVG'] = 0
                summary.loc[summary['Name'] == player, 'SLG'] = 0
            
            # Calculate AvgExitVel if HitCount > 0
            if player_data['HitCount'].sum() > 0:
                summary.loc[summary['Name'] == player, 'AvgExitVel'] = (
                    (player_data['AvgExitVel'] * player_data['HitCount']).sum() / player_data['HitCount'].sum()
                )
            else:
                summary.loc[summary['Name'] == player, 'AvgExitVel'] = 0
            
            # Calculate AvgPitchVel if PitchCount > 0
            if player_data['PitchCount'].sum() > 0:
                summary.loc[summary['Name'] == player, 'AvgPitchVel'] = (
                    (player_data['AvgPitchVel'] * player_data['PitchCount']).sum() / player_data['PitchCount'].sum()
                )
            else:
                summary.loc[summary['Name'] == player, 'AvgPitchVel'] = 0
        
        # Add column to indicate if this is a summary row
        summary['is_summary'] = True
        
        return summary
        
    except Exception as e:
        print(f"Error calculating player summary: {str(e)}")
        return pd.DataFrame()