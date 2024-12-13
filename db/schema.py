# schema.py
import sqlite3
from datetime import datetime

def create_sqlite_schema():
    """Create complete SQLite database schema for HitTrax data"""
    
    conn = sqlite3.connect('hittrax_local.db')
    cursor = conn.cursor()
    
    try:
        # First create your existing tables
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
            Gender INTEGER NOT NULL
        )
        ''')

        # Create Session table (your existing code)
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
            FOREIGN KEY (UserId) REFERENCES Users(Id)
        )
        ''')
        
        # Create Plays table (your existing code)
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
            FOREIGN KEY (SessionId) REFERENCES Session(Id)
        )
        ''')

        # Create the conversion views
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS UsersConverted AS
        SELECT 
            Id,
            UnitId,
            FirstName,
            LastName,
            UserName,
            Password,
            Created,
            Email,
            Stadium,
            SkillLevel,
            CAST(ROUND(Height * 3.28084, 1) AS REAL) as HeightFeet,
            CAST(ROUND(Weight * 2.20462) AS INTEGER) as WeightLbs,
            Active,
            Position,
            Bats,
            Throws,
            School,
            HomeTown,
            GraduationYear,
            Gender,
            BirthDate
        FROM Users
        ''')

        cursor.execute('''
    CREATE VIEW IF NOT EXISTS SessionConverted AS
    SELECT 
        Id,
        UnitId,
        UserId,
        UserUnitId,
        TimeStamp,
        Stadium,
        Type,
        SkillLevel,
        CAST(ROUND(MaxPitchVel * 2.23694, 1) AS REAL) as MaxPitchVelMph,
        CAST(ROUND(MaxExitVel * 2.23694, 1) AS REAL) as MaxExitVelMph,
        CAST(ROUND(AvgPitchVel * 2.23694, 1) AS REAL) as AvgPitchVelMph,
        CAST(ROUND(AvgExitVel * 2.23694, 1) AS REAL) as AvgExitVelMph,
        CAST(ROUND(HHVel * 2.23694, 1) AS REAL) as HHVelMph,
        CAST(ROUND(AvgDistance * 3.28084) AS INTEGER) as AvgDistanceFeet,
        CAST(ROUND(MaxDistance * 3.28084) AS INTEGER) as MaxDistanceFeet,
        CAST(ROUND(MaxGroundDist * 3.28084) AS INTEGER) as MaxGroundDistFeet,
        CAST(ROUND(AvgGroundDist * 3.28084) AS INTEGER) as AvgGroundDistFeet,
        PitchCount,
        HitCount,
        Singles,
        Doubles,
        Triples,
        HomeRuns,
        FoulBalls,
        Strikes,
        Balls,
        AVG,
        SLG,
        LDPercentage,
        FBPercentage,
        GBPercentage,
        LIPercentage,
        ROPercentage,
        COPercentage,
        StrikeZoneBottom,
        StrikeZoneTop,
        HHCount,
        Active,
        StrikeZoneWidth,
        Score,
        MaxPoints,
        AB,
        Video,
        RankMaxVel,
        RankAvgVel,
        RankMaxDist,
        RankPoints,
        BatMaterial
    FROM Session
    ''')
        cursor.execute('''
        CREATE VIEW IF NOT EXISTS PlaysConverted AS
        SELECT 
            Id,
            SessionId,
            TimeStamp,
            CAST(ROUND(ExitBallVel1 * 2.23694, 1) AS REAL) as ExitBallVel1Mph,
            CAST(ROUND(ExitBallVel2 * 2.23694, 1) AS REAL) as ExitBallVel2Mph,
            CAST(ROUND(ExitBallVel3 * 2.23694, 1) AS REAL) as ExitBallVel3Mph,
            CAST(ROUND(PitchVel * 2.23694, 1) AS REAL) as PitchVelMph,
            CAST(ROUND(ExitVelo * 2.23694, 1) AS REAL) as ExitVeloMph,
            CAST(ROUND(Distance * 3.28084) AS INTEGER) as DistanceFeet,
            CAST(ROUND(GroundDist * 3.28084) AS INTEGER) as GroundDistFeet,
            Result,
            Type,
            Fielder,
            Quadrant,
            PitchType,
            Elevation,
            Active,
            Points
        FROM Plays
        ''')

        # Create your existing indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_active ON Users(Active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_skilllevel ON Users(SkillLevel)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_userid ON Session(UserId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_timestamp ON Session(TimeStamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_skilllevel ON Session(SkillLevel)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_active ON Session(Active)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_sessionid ON Plays(SessionId)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_timestamp ON Plays(TimeStamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_exitvelo ON Plays(ExitVelo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_distance ON Plays(Distance)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_plays_active ON Plays(Active)')

        conn.commit()
        print("Successfully created SQLite schema with conversion views")
        
    except Exception as e:
        print(f"Error creating schema: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_sqlite_schema()