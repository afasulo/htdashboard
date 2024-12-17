import sqlite3
from config import HITTRAX_CONFIG

def update_schema():
    conn = sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])
    cursor = conn.cursor()
    
    # Drop and recreate the view
    cursor.executescript('''
    DROP VIEW IF EXISTS UsersConverted;
    
    CREATE VIEW UsersConverted AS
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
    FROM Users;
    ''')
    
    conn.commit()
    conn.close()

update_schema()