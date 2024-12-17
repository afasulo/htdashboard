import argparse
import pymssql
import pandas as pd
from datetime import datetime

# Configuration from your existing config.py
SQL_CONFIG = {
    'server': '192.168.113.172',
    'port': 1337,
    'database': 'HitTrax',
    'user': r'DESKTOP-TLAIKQ6\HitTraxPC',
    'password': 'baseball',
    'tds_version': '7.0',
    'charset': 'UTF-8'
}

def get_user_id_by_name(conn, full_name):
    """Get userId from full name"""
    cursor = conn.cursor(as_dict=True)
    first_name, last_name = full_name.split(' ', 1)
    cursor.execute(
        """
        SELECT Id 
        FROM Users 
        WHERE FirstName = %s AND LastName = %s
        """, 
        (first_name, last_name)
    )
    result = cursor.fetchone()
    return result['Id'] if result else None

def export_player_data(user_identifier, output_dir='.'):
    """Export session and play data for a player"""
    try:
        conn = pymssql.connect(**SQL_CONFIG)
        
        # Determine if input is name or userId
        user_id = None
        if isinstance(user_identifier, str) and ' ' in user_identifier:
            user_id = get_user_id_by_name(conn, user_identifier)
            if not user_id:
                raise ValueError(f"No user found with name: {user_identifier}")
        else:
            user_id = int(user_identifier)
        
        # Get all sessions for the user
        sessions_query = """
        SELECT s.*, u.FirstName, u.LastName
        FROM Session s
        JOIN Users u ON s.UserId = u.Id
        WHERE s.UserId = %s
        ORDER BY s.TimeStamp DESC
        """
        
        sessions_df = pd.read_sql(sessions_query, conn, params=(user_id,))
        
        if sessions_df.empty:
            raise ValueError(f"No sessions found for user ID: {user_id}")
        
        # Get all plays for these sessions
        session_ids = sessions_df['Id'].tolist()
        plays_query = """
        SELECT p.*
        FROM Plays p
        WHERE p.SessionId IN ({})
        ORDER BY p.TimeStamp DESC
        """.format(','.join(['%s'] * len(session_ids)))
        
        plays_df = pd.read_sql(plays_query, conn, params=tuple(session_ids))
        
        # Create filenames with timestamp and player info
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        player_name = f"{sessions_df['FirstName'].iloc[0]}_{sessions_df['LastName'].iloc[0]}"
        
        sessions_filename = f"{output_dir}/{player_name}_sessions_{timestamp}.csv"
        plays_filename = f"{output_dir}/{player_name}_plays_{timestamp}.csv"
        
        # Export to CSV
        sessions_df.to_csv(sessions_filename, index=False)
        plays_df.to_csv(plays_filename, index=False)
        
        print(f"Successfully exported data for {player_name}")
        print(f"Sessions file: {sessions_filename}")
        print(f"Plays file: {plays_filename}")
        print(f"Total sessions: {len(sessions_df)}")
        print(f"Total plays: {len(plays_df)}")
        
    except Exception as e:
        print(f"Error exporting data: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export HitTrax data for a specific player')
    parser.add_argument('identifier', help='Player name (e.g., "John Doe") or userId')
    parser.add_argument('--output', '-o', default='.', help='Output directory for CSV files')
    
    args = parser.parse_args()
    export_player_data(args.identifier, args.output)