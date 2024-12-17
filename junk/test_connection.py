import pymssql
import pandas as pd

def get_hittrax_data():
    settings = {
        'server': '192.168.113.172',
        'port': 1337,
        'database': 'HitTrax',
        'user': r'DESKTOP-TLAIKQ6\HitTraxPC',
        'password': 'baseball',
        'tds_version': '7.0',  # Changed from 7.1 to 7.0
        'charset': 'UTF-8'     # Added explicit charset
    }
    
    conn = pymssql.connect(**settings)
    
    query = """
    SELECT 
        s.UserId,
        s.Triples,
        s.FoulBalls,
        s.HHVel,
        s.LOPercentage,
        s.MaxDistance,
        s.Score,
        s.AVG,
        s.HitCount,
        s.SLG,
        s.MaxExitVel,
        s.HomeRuns,
        s.AvgElevation,
        s.PitchCount,
        s.AvgExitVel,
        s.Doubles,
        s.Singles,
        s.MaxPoints,
        s.AB,
        s.SkillLevel,
        u.FirstName,
        u.LastName
    FROM Session s
    LEFT JOIN Users u ON s.UserId = u.Id
    WHERE s.SkillLevel IS NOT NULL
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Create full name column
    df['Name'] = df['FirstName'] + ' ' + df['LastName']
    return df

def test_connection():
    """Test the database connection with the updated settings."""
    try:
        settings = {
            'server': '192.168.113.172',
            'port': 1337,
            'database': 'HitTrax',
            'user': r'DESKTOP-TLAIKQ6\HitTraxPC',
            'password': 'baseball',
            'tds_version': '7.0',  # Changed from 7.1 to 7.0
            'charset': 'UTF-8'     # Added explicit charset
        }
        
        print("Attempting to connect to database...")
        conn = pymssql.connect(**settings)
        print("Successfully connected to database!")
        
        print("\nTesting query execution...")
        query = "SELECT TOP 1 * FROM Session"
        df = pd.read_sql(query, conn)
        print("Successfully executed query!")
        print(f"Number of columns: {len(df.columns)}")
        print("Column names:", df.columns.tolist())
        
        conn.close()
        print("\nConnection closed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False
    
def analyze_database_size():
    try:
        df = get_hittrax_data()
        memory_usage = df.memory_usage(deep=True).sum() / 1024**2  # Convert to MB
        row_count = len(df)
        column_count = len(df.columns)
        
        print(f"Database Statistics:")
        print(f"Total Rows: {row_count:,}")
        print(f"Total Columns: {column_count}")
        print(f"Memory Usage: {memory_usage:.2f} MB")
        
        # Show size of each column
        column_sizes = df.memory_usage(deep=True)
        print("\nColumn Memory Usage (MB):")
        for col in df.columns:
            size = column_sizes[df.columns.get_loc(col)] / 1024**2
            print(f"{col}: {size:.2f} MB")
            
    except Exception as e:
        print(f"Error analyzing database: {str(e)}")
        
def analyze_database_structure():
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
        cursor = conn.cursor()
        
        # First, get all table names
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        
        tables = cursor.fetchall()
        
        print("\nDatabase Structure Analysis:")
        print("-" * 80)
        print(f"{'Table Name':<30} {'Row Count':<15}")
        print("-" * 80)
        
        total_rows = 0
        
        # For each table, get row count
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            total_rows += row_count
            print(f"{table_name:<30} {row_count:<15,}")
        
        print("-" * 80)
        print(f"{'Total':<30} {total_rows:<15,}")
        
        # Get column information for each table
        print("\nDetailed Table Structure:")
        for (table_name,) in tables:
            print(f"\nTable: {table_name}")
            print("-" * 70)
            
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    IS_NULLABLE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (table_name,))
            
            columns = cursor.fetchall()
            print(f"{'Column Name':<30} {'Data Type':<15} {'Max Length':<15} {'Nullable':<8}")
            print("-" * 70)
            
            for col_name, data_type, max_length, nullable in columns:
                max_length = str(max_length) if max_length is not None else 'N/A'
                print(f"{col_name:<30} {data_type:<15} {max_length:<15} {nullable:<8}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error analyzing database: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_database_structure()