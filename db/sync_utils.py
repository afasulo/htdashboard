import pandas as pd
import sqlite3
from config import HITTRAX_CONFIG

def convert_units(df: pd.DataFrame) -> pd.DataFrame:
    """Convert units in dataframe from metric to imperial"""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    conv = HITTRAX_CONFIG['conversions']
    
    # Dictionary of columns and their conversion factors
    velocity_columns = [
        'MaxPitchVel', 'MaxExitVel', 'AvgPitchVel', 'AvgExitVel', 
        'HHVel', 'ExitBallVel1', 'ExitBallVel2', 'ExitBallVel3',
        'PitchVel', 'ExitVelo'
    ]
    
    distance_columns = [
        'AvgDistance', 'MaxDistance', 'MaxGroundDist', 'AvgGroundDist',
        'Distance', 'GroundDist'
    ]
    
    # Apply conversions only to columns that exist in the dataframe
    for col in velocity_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0) * conv['mps_to_mph']
            
    for col in distance_columns:
        if col in df.columns:
            df[col] = df[col].fillna(0) * conv['meters_to_feet']
    
    return df

def convert_units_before_save(df: pd.DataFrame) -> pd.DataFrame:
    """Keep data in metric - no conversion needed as source is already metric"""
    return df

def log_sync_event(cursor, table_name: str, rows_synced: int, status: str, message: str = None):
    """Log synchronization event"""
    cursor.execute('''
        INSERT INTO SyncLog (TableName, LastSyncTime, RowsSynced, Status, Message)
        VALUES (?, CURRENT_TIMESTAMP, ?, ?, ?)
    ''', (table_name, rows_synced, status, message))

def get_converted_data(table_name: str, conn: sqlite3.Connection, where_clause: str = None) -> pd.DataFrame:
    """Get data from the converted views instead of raw tables"""
    view_name = f"{table_name}Converted"
    query = f"SELECT * FROM {view_name}"
    if where_clause:
        query += f" WHERE {where_clause}"
    return pd.read_sql(query, conn)