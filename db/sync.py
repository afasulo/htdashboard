# sync.py
import pymssql
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from config import HITTRAX_CONFIG
from sync_utils import convert_units, log_sync_event

def sync_users(verbose=True):
    """Sync ALL Users from HitTrax to SQLite"""
    if verbose:
        print("\nSyncing Users table...")
    
    source_conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
    sqlite_conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
    
    try:
        # Get ALL users data
        query = """
        SELECT 
            Id, UnitId, FirstName, LastName, UserName, Password,
            Created, Email, Stadium, SkillLevel, GameType, Height,
            Role, Active, Weight, Position, Bats, Throws,
            School, HomeTown, GraduationYear, Gender, BirthDate  -- Added BirthDate
        FROM Users
        """
        
        if verbose:
            print("Fetching all users from source database...")
        
        df = pd.read_sql(query, source_conn)
        
        if verbose:
            print(f"Found {len(df)} users in source database")
        
        df.to_sql('Users', sqlite_conn, if_exists='replace', index=False)
        
        if verbose:
            print(f"Successfully synced {len(df)} users")
        
        sqlite_conn.commit()
        return len(df)
        
    except Exception as e:
        print(f"Error syncing users: {str(e)}")
        sqlite_conn.rollback()
        raise
    finally:
        source_conn.close()
        sqlite_conn.close()

def sync_sessions(days_back=None, verbose=True):
    """Sync ALL Sessions from HitTrax to SQLite"""
    if verbose:
        print(f"\nSyncing {'all' if days_back is None else f'last {days_back} days of'} Sessions...")
    
    source_conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
    sqlite_conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
    
    try:
        # Build query for all or recent sessions
        base_query = """
        SELECT 
            Id, UnitId, UserId, UserUnitId, TimeStamp, Stadium, Type,
            SkillLevel, GameType, MaxPitchVel, MaxExitVel, AvgPitchVel,
            AvgExitVel, AvgElevation, AvgDistance, MaxDistance, PitchCount,
            HitCount, Singles, Doubles, Triples, HomeRuns, FoulBalls,
            Strikes, Balls, AVG, SLG, LDPercentage, FBPercentage,
            GBPercentage, LIPercentage, RIPercentage, CIPercentage,
            LOPercentage, ROPercentage, COPercentage, StrikeZoneBottom,
            StrikeZoneTop, HHCount, HHVel, Active, StrikeZoneWidth,
            MaxGroundDist, AvgGroundDist, Score, MaxPoints, AB, Video,
            RankMaxVel, RankAvgVel, RankMaxDist, RankPoints, BatMaterial
        FROM Session 
        """
        
        params = None
        if days_back is not None:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            base_query += " WHERE TimeStamp >= %s"
            params = (cutoff_date,)
            
        if verbose:
            print("Fetching sessions from source database...")
            
        df = pd.read_sql(base_query, source_conn, params=params)
        
        if verbose:
            print(f"Found {len(df)} sessions in source database")
            
        if verbose:
            print("Converting units...")
            
        df = convert_units(df)
        
        if verbose:
            print("Writing sessions to local database...")
            
        df.to_sql('Session', sqlite_conn, if_exists='replace', index=False)
        
        if verbose:
            print(f"Successfully synced {len(df)} sessions")
        
        sqlite_conn.commit()
        return len(df)
        
    except Exception as e:
        print(f"Error syncing sessions: {str(e)}")
        sqlite_conn.rollback()
        raise
    finally:
        source_conn.close()
        sqlite_conn.close()

def sync_plays(days_back=None, verbose=True):
    """Sync ALL Plays from HitTrax to SQLite"""
    if verbose:
        print(f"\nSyncing {'all' if days_back is None else f'last {days_back} days of'} Plays...")
    
    source_conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
    sqlite_conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
    
    try:
        # Build query for all or recent plays
        base_query = """
        SELECT 
            Id, SessionId, TimeStamp, ExitBallVel1, ExitBallVel2,
            ExitBallVel3, Distance, PitchVel, Result, Type, Fielder,
            Quadrant, PosStart1, PosStart2, PosStart3, PosEnd1, PosEnd2,
            PosEnd3, PosPitch1, PosPitch2, PosPitch3, PosCaught1,
            PosCaught2, PosCaught3, PitchType, PitchCoeffs1, PitchCoeffs2,
            PitchCoeffs3, PitchCoeffs4, PitchCoeffs5, PitchCoeffs6,
            PitchBreakH, PitchBreakV, Elevation, PitchBreakVG, Ms,
            GroundDist, Active, Intersect1, Intersect2, Intersect3,
            PitchAngle, HorizontalAngle, ExitVelo, Points
        FROM Plays 
        """
        
        params = None
        if days_back is not None:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            base_query += " WHERE TimeStamp >= %s"
            params = (cutoff_date,)
            
        if verbose:
            print("Fetching plays from source database...")
            
        df = pd.read_sql(base_query, source_conn, params=params)
        
        if verbose:
            print(f"Found {len(df)} plays in source database")
            
        if verbose:
            print("Converting units...")
            
        df = convert_units(df)
        
        if verbose:
            print("Writing plays to local database...")
            
        df.to_sql('Plays', sqlite_conn, if_exists='replace', index=False)
        
        if verbose:
            print(f"Successfully synced {len(df)} plays")
        
        sqlite_conn.commit()
        return len(df)
        
    except Exception as e:
        print(f"Error syncing plays: {str(e)}")
        sqlite_conn.rollback()
        raise
    finally:
        source_conn.close()
        sqlite_conn.close()

def sync_all(days_back=None):
    """Run full synchronization"""
    print("Starting full sync...")
    print("Note: This will sync ALL historical data and may take a while...")
    
    if not test_source_connection():
        print("Failed to connect to source database. Aborting sync.")
        return
    
    try:
        users_count = sync_users()
        sessions_count = sync_sessions(days_back)
        plays_count = sync_plays(days_back)
        
        print("\nSync complete!")
        print(f"Synced:")
        print(f"- {users_count:,} users")
        print(f"- {sessions_count:,} sessions")
        print(f"- {plays_count:,} plays")
        
        verify_data()
        
    except Exception as e:
        print(f"Error during sync: {str(e)}")
        
def test_source_connection():
    """Test connection to source HitTrax database"""
    try:
        print("Testing connection to HitTrax database...")
        conn = pymssql.connect(**HITTRAX_CONFIG['source_db'])
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT COUNT(*) FROM Users")
        count = cursor.fetchone()[0]
        print(f"Connection successful! Found {count} users in source database.")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to HitTrax database: {str(e)}")
        return False

def sync_all(days_back=None):
    """Run full synchronization"""
    print("Starting full sync...")
    print("Note: This will sync ALL historical data and may take a while...")
    
    try:
        users_count = sync_users()
        sessions_count = sync_sessions(days_back)
        plays_count = sync_plays(days_back)
        
        print("\nSync complete!")
        print(f"Synced:")
        print(f"- {users_count:,} users")
        print(f"- {sessions_count:,} sessions")
        print(f"- {plays_count:,} plays")
        
    except Exception as e:
        print(f"Error during sync: {str(e)}")

if __name__ == "__main__":
    # Sync ALL historical data
    sync_all(days_back=None)