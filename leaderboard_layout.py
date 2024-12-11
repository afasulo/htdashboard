# leaderboard_layout.py
from dash import html, dcc

def create_leaderboard_date_filter():
    return html.Div([
        html.Div([
            html.Label('Select Date Range:'),
            dcc.DatePickerRange(
                id='leaderboard-date-filter',
                style={'marginTop': '10px'}
            )
        ], style={
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '5px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'marginBottom': '20px'
        })
    ])

def create_player_card(player_data):
    rank_styles = {
        1: {'backgroundColor': '#FFD700', 'color': 'black'},  # Gold
        2: {'backgroundColor': '#C0C0C0', 'color': 'black'},  # Silver
        3: {'backgroundColor': '#CD7F32', 'color': 'white'},  # Bronze
        'default': {'backgroundColor': '#f0f0f0', 'color': 'black'}
    }
    
    rank_style = rank_styles.get(player_data['rank'], rank_styles['default'])
    
    return html.Div([
        # Rank and Name Header
        html.Div([
            html.Div(
                str(player_data['rank']),
                style={
                    'width': '30px',
                    'height': '30px',
                    'borderRadius': '50%',
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'fontWeight': 'bold',
                    **rank_style,
                    'marginRight': '10px'
                }
            ),
            html.H4(player_data['name'], style={'fontWeight': 'bold', 'fontSize': '1.2em', 'margin': '0'}),
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
        
        # School
        html.P(player_data['school'], style={'color': '#666', 'margin': '5px 0'}),
        
        # Main Stat
        html.Div(
            f"{player_data['value']:.1f} {player_data['unit']}",
            style={'fontSize': '1.5em', 'fontWeight': 'bold', 'color': '#2c5282', 'margin': '10px 0'}
        ),
        
        # Additional Stats
        html.Div([
            html.Div([
                html.Span('AB: ', style={'color': '#666'}),
                html.Span(f"{player_data['total_abs']}"),
            ], style={'marginRight': '15px'}),
            html.Div([
                html.Span('AVG: ', style={'color': '#666'}),
                html.Span(f"{player_data['batting_avg']:.3f}"),
            ], style={'marginRight': '15px'}),
            html.Div([
                html.Span('SLG: ', style={'color': '#666'}),
                html.Span(f"{player_data['slg_pct']:.3f}"),
            ], style={'marginRight': '15px'}),
            html.Div([
                html.Span('HR: ', style={'color': '#666'}),
                html.Span(f"{player_data['home_runs']}"),
            ]),
        ], style={'display': 'flex', 'flexWrap': 'wrap'})
    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '5px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '15px'
    })

def create_metric_section(metric_title, metric_id):
    return html.Div([
        html.H3(metric_title, style={
            'fontSize': '1.5em',
            'fontWeight': 'bold',
            'marginBottom': '20px'
        }),
        
        dcc.Tabs(
            id=f'grad-year-tabs-{metric_id}',
            value='2025',
            children=[
                dcc.Tab(
                    label=str(year),
                    value=str(year),
                    style={
                        'padding': '10px 15px',
                        'backgroundColor': '#f8f9fa',
                        'borderBottom': '1px solid #dee2e6'
                    },
                    selected_style={
                        'padding': '10px 15px',
                        'backgroundColor': 'white',
                        'borderBottom': '2px solid #2c5282',
                        'color': '#2c5282',
                        'fontWeight': 'bold'
                    }
                ) for year in range(2025, 2035)
            ]
        ),
        
        html.Div(
            id=f'leaderboard-content-{metric_id}',
            style={'padding': '20px 0'}
        )
    ], style={
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '5px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'marginBottom': '30px'
    })

def create_leaderboard_layout():
    return html.Div([
        html.H1("Baseball Performance Leaderboards", style={
            'textAlign': 'center',
            'fontSize': '2em',
            'fontWeight': 'bold',
            'margin': '30px 0'
        }),
        
        create_leaderboard_date_filter(),
        
        html.Div([
            create_metric_section("Max Exit Velocity", "max-exit-velocity"),
            create_metric_section("Average Exit Velocity", "average-exit-velocity"),
            create_metric_section("Max Distance", "max-distance"),
            create_metric_section("Average Distance", "average-distance")
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(450px, 1fr))',
            'gap': '20px',
            'padding': '20px'
        })
    ], style={
        'maxWidth': '1800px',
        'margin': '0 auto',
        'padding': '20px'
    })