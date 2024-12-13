import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import base64
import os
from layouts import create_hittrax_analysis_tab
from callbacks import register_hittrax_callbacks, register_leaderboard_callbacks
from leaderboard_layout import create_leaderboard_layout
from sqlite_utils import get_hittrax_data, calculate_player_stats
from config import HITTRAX_CONFIG

# Database verification
def verify_database():
    print("\n=== Database Verification ===")
    
    # Check if database file exists
    db_path = HITTRAX_CONFIG['sqlite_db']
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / (1024 * 1024)  # Size in MB
        print(f"SQLite database exists at {os.path.abspath(db_path)}")
        print(f"Database size: {size:.2f} MB")
        
        # Test data retrieval
        try:
            print("\nTesting data retrieval...")
            df = get_hittrax_data()
            if not df.empty:
                print(f"Successfully retrieved {len(df)} records")
                print("Sample columns:", list(df.columns)[:5])
                
                # Test stats calculation
                stats_df = calculate_player_stats(df, min_ab=10)
                print(f"\nCalculated stats for {len(stats_df)} players with 10+ at-bats")
                if not stats_df.empty:
                    print("Sample player stats columns:", list(stats_df.columns))
            else:
                print("Warning: No data retrieved from database")
        except Exception as e:
            print(f"Error accessing database: {str(e)}")
    else:
        print("Warning: Database file not found!")
    
    print("=== Verification Complete ===\n")

# Run verification before starting app
verify_database()

app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ],
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    html.H1("Baseball Analysis Dashboard", style={'textAlign': 'center'}),
    
    dcc.Tabs([
        dcc.Tab(label='HitTrax Analysis', children=[
            create_hittrax_analysis_tab()
        ]),
        
        dcc.Tab(label='Leaderboards', children=[
            create_leaderboard_layout()
        ])
    ])
])

# Register callbacks
app = register_hittrax_callbacks(app)
app = register_leaderboard_callbacks(app)

if __name__ == '__main__':
    print("Starting the dashboard... Open http://127.0.0.1:8050/ in your web browser")
    app.run_server(debug=True)