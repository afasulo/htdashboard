import sqlite3
from datetime import datetime

def create_sqlite_schema():
    """Create complete SQLite database schema for HitTrax data"""
    
    conn = sqlite3.connect('hittrax_local.db')
    cursor = conn.cursor()
    
    try:
        # Create Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            Id INTEGER PRIMARY KEY,
            UnitId INTEGER NOT NULL,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            UserName TEXT NOT NULL,
            Password TEXT NOT NULL,
            Created TIMESTAMP,
            Email TEXT,
            Stadium INTEGER NOT NULL,
            SkillLevel INTEGER NOT NULL,
            GameType INTEGER NOT NULL,
            Height REAL NOT NULL,
            Role INTEGER NOT NULL,
            Active INTEGER NOT NULL,
            Weight REAL NOT NULL,
            Position INTEGER NOT NULL,
            Bats INTEGER NOT NULL,
            Throws INTEGER NOT NULL,
            School TEXT NOT NULL,
            HomeTown TEXT NOT NULL,
            GraduationYear INTEGER NOT NULL,
            Gender INTEGER NOT NULL,
            LastSynced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create Session table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Session (
            Id INTEGER PRIMARY KEY,
            UnitId INTEGER NOT NULL,
            UserId INTEGER NOT NULL,
            UserUnitId INTEGER NOT NULL,
            TimeStamp TIMESTAMP NOT NULL,
            Stadium INTEGER NOT NULL,
            Type INTEGER NOT NULL,
            SkillLevel INTEGER NOT NULL,
            GameType INTEGER NOT NULL,
            MaxPitchVel REAL NOT NULL,
            MaxExitVel REAL NOT NULL,
            AvgPitchVel REAL NOT NULL,
            AvgExitVel REAL NOT NULL,
            AvgElevation REAL NOT NULL,
            AvgDistance REAL NOT NULL,
            MaxDistance REAL NOT NULL,
            PitchCount INTEGER NOT NULL,
            HitCount INTEGER NOT NULL,
            Singles INTEGER NOT NULL,
            Doubles INTEGER NOT NULL,
            Triples INTEGER NOT NULL,
            HomeRuns INTEGER NOT NULL,
            FoulBalls INTEGER NOT NULL,
            Strikes INTEGER NOT NULL,
            Balls INTEGER NOT NULL,
            AVG REAL NOT NULL,
            SLG REAL NOT NULL,
            LDPercentage REAL NOT NULL,
            FBPercentage REAL NOT NULL,
            GBPercentage REAL NOT NULL,
            LIPercentage REAL NOT NULL,
            RIPercentage REAL NOT NULL,
            CIPercentage REAL NOT NULL,
            LOPercentage REAL NOT NULL,
            ROPercentage REAL NOT NULL,
            COPercentage REAL NOT NULL,
            StrikeZoneBottom REAL NOT NULL,
            StrikeZoneTop REAL NOT NULL,
            HHCount INTEGER NOT NULL,
            HHVel REAL NOT NULL,
            Active INTEGER NOT NULL,
            StrikeZoneWidth REAL NOT NULL,
            MaxGroundDist REAL NOT NULL,
            AvgGroundDist REAL NOT NULL,
            Score INTEGER NOT NULL,
            MaxPoints INTEGER NOT NULL,
            AB INTEGER NOT NULL,
            Video INTEGER NOT NULL,
            RankMaxVel REAL NOT NULL,
            RankAvgVel REAL NOT NULL,
            RankMaxDist REAL NOT NULL,
            RankPoints REAL NOT NULL,
            BatMaterial INTEGER NOT NULL,
            LastSynced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (UserId) REFERENCES Users(Id)
        )
        ''')
        
        # Create Plays table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Plays (
            Id INTEGER PRIMARY KEY,
            SessionId INTEGER NOT NULL,
            TimeStamp TIMESTAMP NOT NULL,
            ExitBallVel1 REAL NOT NULL,
            ExitBallVel2 REAL NOT NULL,
            ExitBallVel3 REAL NOT NULL,
            Distance REAL NOT NULL,
            PitchVel REAL NOT NULL,
            Result INTEGER NOT NULL,
            Type INTEGER NOT NULL,
            Fielder INTEGER NOT NULL,
            Quadrant INTEGER NOT NULL,
            PosStart1 REAL NOT NULL,
            PosStart2 REAL NOT NULL,
            PosStart3 REAL NOT NULL,
            PosEnd1 REAL NOT NULL,
            PosEnd2 REAL NOT NULL,
            PosEnd3 REAL NOT NULL,
            PosPitch1 REAL NOT NULL,
            PosPitch2 REAL NOT NULL,
            PosPitch3 REAL NOT NULL,
            PosCaught1 REAL NOT NULL,
            PosCaught2 REAL NOT NULL,
            PosCaught3 REAL NOT NULL,
            PitchType INTEGER NOT NULL,
            PitchCoeffs1 REAL NOT NULL,
            PitchCoeffs2 REAL NOT NULL,
            PitchCoeffs3 REAL NOT NULL,
            PitchCoeffs4 REAL NOT NULL,
            PitchCoeffs5 REAL NOT NULL,
            PitchCoeffs6 REAL NOT NULL,
            PitchBreakH REAL NOT NULL,
            PitchBreakV REAL NOT NULL,
            Elevation REAL NOT NULL,
            PitchBreakVG REAL NOT NULL,
            Ms INTEGER NOT NULL,
            GroundDist REAL NOT NULL,
            Active INTEGER NOT NULL,
            Intersect1 REAL NOT NULL,
            Intersect2 REAL NOT NULL,
            Intersect3 REAL NOT NULL,
            PitchAngle REAL NOT NULL,
            HorizontalAngle REAL NOT NULL,
            ExitVelo REAL NOT NULL,
            Points INTEGER NOT NULL,
            LastSynced TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (SessionId) REFERENCES Session(Id)
        )
        ''')
        
        # Create indices for Users table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON Users(Active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_skilllevel ON Users(SkillLevel)')
        
        # Create indices for Session table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_userid ON Session(UserId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON Session(TimeStamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_skilllevel ON Session(SkillLevel)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_active ON Session(Active)')
        
        # Create indices for Plays table
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_sessionid ON Plays(SessionId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_timestamp ON Plays(TimeStamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_exitvelo ON Plays(ExitVelo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_distance ON Plays(Distance)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_active ON Plays(Active)')
        
        # Create sync tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS SyncLog (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            TableName TEXT NOT NULL,
            LastSyncTime TIMESTAMP NOT NULL,
            RowsSynced INTEGER NOT NULL,
            Status TEXT NOT NULL,
            Message TEXT
        )
        ''')
        
        conn.commit()
        print("Successfully created SQLite schema")
        
    except Exception as e:
        print(f"Error creating schema: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_sqlite_schema()