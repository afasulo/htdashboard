import sqlite3
import pandas as pd
from config import HITTRAX_CONFIG

def get_db_connection():
    """Create a connection to the SQLite database"""
    return sqlite3.connect(HITTRAX_CONFIG['sqlite_db'])

def get_leaderboard_data(start_date=None, end_date=None, min_ab=50):
    """Get leaderboard data for each metric by graduation year"""
    try:
        conn = get_db_connection()
        
        # Debug print to verify connection
        print("Database connection established")
        
        query = """
        WITH PlayerStats AS (
            SELECT 
                u.FirstName || ' ' || u.LastName as Name,
                u.School,
                u.BirthDate,
                CASE 
                    WHEN u.FirstName || ' ' || u.LastName = 'Brody Armstrong' THEN 2029
                    WHEN u.GraduationYear IS NOT NULL AND u.GraduationYear != 1 THEN u.GraduationYear
                    WHEN u.FirstName || ' ' || u.LastName = 'Colton Floyd' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Maddox Gonzales' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Kaiden Nerhood' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Wyatt Tinker' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Dean Ellison' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Aiden Mobley' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Everett Burdett' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Luke Feist' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Chase Qualler' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Edward Blanshine' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Damon Saavedra' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Abram Pine' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Noah Segura' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Hunter Easton' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Chris Moya' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Nathaniel Jaramillo' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Mark Scime' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Deegan Goldberg' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Ty Rector' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Avery Dearholt' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Chris Moya' THEN 2026
                    WHEN u.FirstName || ' ' || u.LastName = 'Landyn Cottone' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Caiden House' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Tas Lupo' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Logan Sunstrom' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Brayden Bustillos' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Chase Rivera' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Matthew Cook' THEN 2027
                    WHEN u.FirstName || ' ' || u.LastName = 'Richie Reiffenberger' THEN 2028
                    WHEN u.FirstName || ' ' || u.LastName = 'Brayden Palmerton' THEN 2028
                    WHEN u.FirstName || ' ' || u.LastName = 'Drew Jones' THEN 2029
                    WHEN u.FirstName || ' ' || u.LastName = 'James Tabbert' THEN 2029
                    WHEN u.FirstName || ' ' || u.LastName = 'Gavin Eaton' THEN 2029
                    WHEN u.FirstName || ' ' || u.LastName = 'Tyler Worthen' THEN 2029
                    WHEN u.FirstName || ' ' || u.LastName = 'Calin Rivera' THEN 2029
                    WHEN u.FirstName || ' ' || u.LastName = 'Aiden Koester' THEN 2030
                    WHEN u.FirstName || ' ' || u.LastName = 'Aaron Flores' THEN 2030
                    WHEN u.FirstName || ' ' || u.LastName = 'Brody Armstrong' THEN 2030
                    WHEN u.FirstName || ' ' || u.LastName = 'Adam Jimenez' THEN 2023
                    WHEN u.FirstName || ' ' || u.LastName = 'Jace Gabaldon' THEN 2028
                    WHEN u.FirstName || ' ' || u.LastName = 'Radley Philipbar' THEN 2028
                    WHEN strftime('%m', u.BirthDate) >= '09' 
                    THEN cast(strftime('%Y', u.BirthDate) as integer) + 18 
                    ELSE cast(strftime('%Y', u.BirthDate) as integer) + 17 
                END as GradYear,
                MAX(s.MaxExitVelMph) as MaxExitVelo,
                AVG(s.AvgExitVelMph) as AvgExitVelo,
                MAX(s.MaxDistanceFeet) as MaxDistance,
                AVG(s.AvgDistanceFeet) as AvgDistance,
                SUM(s.AB) as TotalAB,
                AVG(s.AVG) as BattingAvg,
                AVG(s.SLG) as SlugPct,
                SUM(s.HomeRuns) as HomeRuns
            FROM UsersConverted u
            JOIN SessionConverted s ON u.Id = s.UserId
            WHERE s.TimeStamp BETWEEN COALESCE(?, date('now', '-1 year')) AND COALESCE(?, date('now'))
                AND s.Active = 1
            GROUP BY u.FirstName, u.LastName, u.School, u.BirthDate, u.GraduationYear
            HAVING SUM(s.AB) >= ?
        )
        SELECT 
            Name,
            School,
            GradYear,
            MaxExitVelo,
            AvgExitVelo,
            MaxDistance,
            AvgDistance,
            TotalAB,
            BattingAvg,
            SlugPct,
            HomeRuns,
            ROW_NUMBER() OVER (PARTITION BY GradYear ORDER BY MaxExitVelo DESC) as MaxExitVeloRank,
            ROW_NUMBER() OVER (PARTITION BY GradYear ORDER BY AvgExitVelo DESC) as AvgExitVeloRank,
            ROW_NUMBER() OVER (PARTITION BY GradYear ORDER BY MaxDistance DESC) as MaxDistanceRank,
            ROW_NUMBER() OVER (PARTITION BY GradYear ORDER BY AvgDistance DESC) as AvgDistanceRank
        FROM PlayerStats
        WHERE GradYear BETWEEN 2025 AND 2034
        ORDER BY GradYear, MaxExitVeloRank, AvgExitVeloRank, MaxDistanceRank, AvgDistanceRank
        """
        
        # Debug print before executing query
        print("Executing query...")
        
        df = pd.read_sql(query, conn, params=(start_date, end_date, min_ab))
        
        # Debug print after query execution
        print(f"Query returned {len(df)} rows")
        
        conn.close()
        
        metrics = {
            'max-exit-velocity': {'field': 'MaxExitVelo', 'rank': 'MaxExitVeloRank', 'unit': 'mph'},
            'average-exit-velocity': {'field': 'AvgExitVelo', 'rank': 'AvgExitVeloRank', 'unit': 'mph'},
            'max-distance': {'field': 'MaxDistance', 'rank': 'MaxDistanceRank', 'unit': 'ft'},
            'average-distance': {'field': 'AvgDistance', 'rank': 'AvgDistanceRank', 'unit': 'ft'}
        }
        
        result = {}
        for metric_key, config in metrics.items():
            result[metric_key] = {year: [] for year in range(2025, 2035)}
            
            for year in range(2025, 2035):
                year_df = df[df['GradYear'] == year].copy()
                top_5 = year_df[year_df[config['rank']] <= 5].sort_values(config['rank'])
                
                for _, row in top_5.iterrows():
                    result[metric_key][year].append({
                        'name': row['Name'],
                        'school': row['School'],
                        'value': row[config['field']],
                        'unit': config['unit'],
                        'total_abs': row['TotalAB'],
                        'batting_avg': row['BattingAvg'],
                        'slg_pct': row['SlugPct'],
                        'home_runs': row['HomeRuns'],
                        'rank': int(row[config['rank']])
                    })
        
        return result
        
    except Exception as e:
        print(f"Error getting leaderboard data: {str(e)}")
        return {}

if __name__ == "__main__":
    # Add some basic testing code
    print("Testing leaderboard data retrieval...")
    result = get_leaderboard_data()
    print(f"Retrieved data for {len(result)} metrics")
    for metric, years in result.items():
        for year, players in years.items():
            if players:
                print(f"{metric} - {year}: {len(players)} players")