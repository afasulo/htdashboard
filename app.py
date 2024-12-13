import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import base64
from layouts import create_hittrax_filters, create_hittrax_graphs, create_hittrax_analysis_tab
from callbacks import register_hittrax_callbacks, register_leaderboard_callbacks  # Added import
from leaderboard_layout import create_leaderboard_layout

# Initialize the app with suppress_callback_exceptions=True
app = dash.Dash(
    __name__,
    external_stylesheets=[
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
    ]
)

app.layout = html.Div([
    html.H1("Baseball Analysis Dashboard", style={'textAlign': 'center'}),
    
    dcc.Tabs([
        dcc.Tab(label='Group Analysis', children=[
            # Original layout...
        ]),
        
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