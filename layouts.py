from dash import html, dcc, dash_table
from utils import COLUMN_GROUPS

def create_hittrax_filters():
    return html.Div([
        html.Div([
            html.Label('Select Skill Level:'),
            dcc.Dropdown(
                id='skill-level-filter',
                multi=True,
                placeholder="Select skill level"
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
        
        html.Div([
            html.Label('Select Players:'),
            dcc.Dropdown(
                id='hittrax-player-filter',
                multi=True,
                placeholder="Select specific players"
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
        
        html.Div([
            html.Label('Minimum At Bats:'),
            dcc.Input(
                id='min-ab-filter',
                type='number',
                value=10,
                min=1
            )
        ], style={'width': '20%', 'display': 'inline-block'})
    ], style={'margin': '20px'})

def create_hittrax_table():
    return html.Div([
        # Summary Table
        html.Div([
            html.H3("Player Summaries"),
            dash_table.DataTable(
                id='hittrax-summary-table',
                page_size=15,
                page_action='native',
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                filter_options={'case': 'insensitive'},
                row_selectable='single',  # Allow selecting one row at a time
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid black'
                },
                tooltip_delay=0,
                tooltip_duration=None,  # Tooltip stays visible until mouse leaves
                css=[{
                    'selector': '.dash-table-tooltip',
                    'rule': 'background-color: white; font-size: 12px; padding: 5px;'
                }]
            )
        ]),
        
        # Detail Modal
        html.Div([  # Modal container
            html.Div(
                id='session-detail-modal',
                className='modal',
                style={
                    'display': 'none',  # Initially hidden
                    'position': 'fixed',
                    'zIndex': 1000,
                    'left': 0,
                    'top': 0,
                    'width': '100%',
                    'height': '100%',
                    'overflow': 'auto',
                    'backgroundColor': 'rgba(0,0,0,0.4)',
                },
                children=[
                    html.Div([  # Modal content
                        html.H3("Session Details", style={'marginBottom': '20px'}),
                        dash_table.DataTable(
                            id='session-detail-table',
                            page_size=10,
                            page_action='native',
                            sort_action='native',
                            sort_mode='multi',
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '8px',
                                'minWidth': '100px'
                            },
                            style_header={
                                'backgroundColor': 'rgb(230, 230, 230)',
                                'fontWeight': 'bold'
                            }
                        ),
                        html.Button(
                            "Close",
                            id="close-modal",
                            style={'marginTop': '20px'}
                        )
                    ], style={
                        'backgroundColor': 'white',
                        'margin': '10% auto',
                        'padding': '20px',
                        'width': '80%',
                        'maxWidth': '1200px',
                        'borderRadius': '5px',
                    })
                ]
            )
        ])
    ])

def create_hittrax_graphs():
    return html.Div([
        dcc.Graph(id='exit-velo-distance-scatter', style={'height': '600px'}),
        html.Div([
            dcc.Graph(id='batting-stats-radar', style={'display': 'inline-block', 'width': '50%'}),
            dcc.Graph(id='exit-velo-boxplot', style={'display': 'inline-block', 'width': '50%'})
        ])
    ])

def create_column_selector():
    return html.Div([
        html.Label('Select Columns to Display:', style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Dropdown(
            id='column-display-selector',  # Changed to match callback
            options=[{'label': col, 'value': col} for group in COLUMN_GROUPS.values() for col in group],
            value=[col for group in COLUMN_GROUPS.values() for col in group],  # All columns selected by default
            multi=True,
            placeholder="Select columns to display",
            style={'width': '100%'}
        )
    ], style={'margin': '20px', 'width': '100%'})

def create_session_details_layout():
    """Create a comprehensive session details layout"""
    return html.Div([
        # Header with player info and controls
        html.Div([
            html.H2(id='player-name-header', style={'display': 'inline-block'}),
            html.Button(
                '← Back to Summary', 
                id='return-to-summary',
                style={
                    'float': 'right',
                    'margin': '10px',
                    'padding': '10px',
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #ddd',
                    'borderRadius': '4px'
                }
            ),
        ], style={'marginBottom': '20px', 'padding': '10px'}),
        
        # Session Filters
        html.Div([
            html.Div([
                html.Label('Date Range:'),
                dcc.DatePickerRange(
                    id='session-date-filter',
                    style={'marginBottom': '10px'}
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Stats Filter:'),
                dcc.Dropdown(
                    id='session-stats-filter',
                    multi=True,
                    placeholder="Select stats to display"
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Div([
                html.Button(
                    'Export to CSV', 
                    id='export-session-data',
                    style={
                        'marginTop': '20px',
                        'padding': '10px',
                        'backgroundColor': '#28a745',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px'
                    }
                )
            ], style={'width': '20%', 'display': 'inline-block'})
        ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f8f9fa'}),
        
        # Session Analytics
        html.Div([
            html.H3("Performance Trends"),
            dcc.Graph(id='session-trend-graph'),
            
            html.Div([
                dcc.Graph(id='session-heatmap', style={'display': 'inline-block', 'width': '50%'}),
                dcc.Graph(id='session-metrics-chart', style={'display': 'inline-block', 'width': '50%'})
            ])
        ], style={'marginBottom': '20px'}),
        
        # Detailed Session Table
        html.Div([
            html.H3("Session Details"),
            dash_table.DataTable(
                id='session-details-table',  # Make sure this ID is consistent
                page_size=15,
                page_action='native',
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                filter_options={'case': 'insensitive'},
                export_format='csv',
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid black'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ])
    ])

def create_hittrax_analysis_tab():
    return html.Div([
        # Main container that will switch between summary and details
        html.Div(id='main-content', children=[
            # Summary View
            html.Div(id='summary-view', children=[
                create_hittrax_filters(),
                create_column_selector(),
                create_hittrax_graphs(),
                create_hittrax_table()
            ]),
            
            # Session Details View (initially hidden)
            html.Div(id='session-details-view', style={'display': 'none'}, children=[
                create_session_details_layout()
            ])
        ])
    ])
    
def create_session_details_layout():
    """Create a comprehensive session details layout"""
    return html.Div([
        # Header with player info and controls
        html.Div([
            html.H2(id='player-name-header', style={'display': 'inline-block'}),
            html.Button(
                '← Back to Summary', 
                id='return-to-summary',
                style={
                    'float': 'right',
                    'margin': '10px',
                    'padding': '10px',
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #ddd',
                    'borderRadius': '4px'
                }
            ),
        ], style={'marginBottom': '20px', 'padding': '10px'}),
        
        # Session Filters
        html.Div([
            html.Div([
                html.Label('Date Range:'),
                dcc.DatePickerRange(
                    id='session-date-filter',
                    style={'marginBottom': '10px'}
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Stats Filter:'),
                dcc.Dropdown(
                    id='session-stats-filter',
                    multi=True,
                    placeholder="Select stats to display"
                )
            ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),
            
            html.Div([
                html.Button(
                    'Export to CSV', 
                    id='export-session-data',
                    style={
                        'marginTop': '20px',
                        'padding': '10px',
                        'backgroundColor': '#28a745',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px'
                    }
                )
            ], style={'width': '20%', 'display': 'inline-block'})
        ], style={'marginBottom': '20px', 'padding': '10px', 'backgroundColor': '#f8f9fa'}),
        
        # Session Analytics
        html.Div([
            html.H3("Performance Trends"),
            dcc.Graph(id='session-trend-graph'),
            
            html.Div([
                dcc.Graph(id='session-heatmap', style={'display': 'inline-block', 'width': '50%'}),
                dcc.Graph(id='session-metrics-chart', style={'display': 'inline-block', 'width': '50%'})
            ])
        ], style={'marginBottom': '20px'}),
        
        # Detailed Session Table
        html.Div([
            html.H3("Session Details"),
            dash_table.DataTable(  # This must be a DataTable, not a Div
                id='session-details-table',
                page_size=15,
                page_action='native',
                sort_action='native',
                sort_mode='multi',
                filter_action='native',
                filter_options={'case': 'insensitive'},
                export_format='csv',
                style_table={
                    'overflowX': 'auto',
                    'minWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'minWidth': '100px',
                    'maxWidth': '300px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center',
                    'border': '1px solid black'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(248, 248, 248)'
                    }
                ]
            )
        ])
    ])