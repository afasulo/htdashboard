from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from dash import html, callback_context, dash_table
import pandas as pd
from sqlite_utils import get_hittrax_data, calculate_player_stats, get_player_details
from utils import COLUMN_FORMATS, COLUMN_GROUPS
from leaderboard_utils import get_leaderboard_data  # Add this import
from leaderboard_layout import create_player_card  # Add this import


def register_hittrax_callbacks(app):
    
    @app.callback(
        [Output('hittrax-summary-table', 'data'),
         Output('hittrax-summary-table', 'columns'),
         Output('hittrax-summary-table', 'tooltip_data'),
         Output('exit-velo-distance-scatter', 'figure'),
         Output('batting-stats-radar', 'figure'),
         Output('exit-velo-boxplot', 'figure'),
         Output('hittrax-player-filter', 'options'),
         Output('skill-level-filter', 'options')],
        [Input('skill-level-filter', 'value'),
         Input('hittrax-player-filter', 'value'),
         Input('min-ab-filter', 'value'),
         Input('column-display-selector', 'value')]
    )
    def update_hittrax_data(selected_skills, selected_players, min_ab, selected_columns):
        try:
            # Get data and calculate summaries
            df = get_hittrax_data()
            if df.empty:
                raise ValueError("No data available in local database")
            
            stats_df = calculate_player_stats(df, min_ab or 10)
            if stats_df.empty:
                raise ValueError("No qualified players found")

            # Initialize display_data
            display_data = stats_df.copy()

            # Apply filters
            if selected_skills:
                display_data = display_data[display_data['SkillLevel'].isin(selected_skills)]
            if selected_players:
                display_data = display_data[display_data['Name'].isin(selected_players)]

            if display_data.empty:
                empty_fig = px.scatter(title="No data available for selected filters")
                player_options = [{'label': name, 'value': name} for name in sorted(stats_df['Name'].unique())]
                skill_options = [{'label': str(int(skill)), 'value': skill} 
                               for skill in sorted(df['SkillLevel'].unique()) if pd.notna(skill)]
                return [], [], [], empty_fig, empty_fig, empty_fig, player_options, skill_options

            # Format columns and create tooltips for the table
            if not selected_columns:
                selected_columns = [col for group in COLUMN_GROUPS.values() for col in group]

            tooltip_data = []
            for idx in range(len(display_data)):
                row_tooltips = {}
                for col in selected_columns:
                    for format_type, config in COLUMN_FORMATS.items():
                        if col in config['columns']:
                            row_tooltips[col] = {'type': 'text', 'value': config['tooltip']}
                tooltip_data.append(row_tooltips)

            # Create columns configuration
            columns = [
                {'name': col, 'id': col, 'deletable': True, 'selectable': True}
                for col in selected_columns if col in display_data.columns
            ]

            # Create scatter plot
            scatter_fig = px.scatter(
                display_data, 
                x='AvgExitVel', 
                y='MaxDistance',
                color='SkillLevel',
                size='AB',
                hover_data=['Name', 'AVG', 'SLG', 'HomeRuns', 'AB', 'HitCount'],
                text='Name',
                title='Exit Velocity vs Distance by Skill Level'
            )
            scatter_fig.update_traces(textposition='top center')
            
            # Create radar chart
            radar_fig = go.Figure()
            top_players = display_data.nlargest(5, 'AvgExitVel')
            
            for _, player in top_players.iterrows():
                radar_fig.add_trace(go.Scatterpolar(
                    r=[player['AVG'], player['SLG'], 
                       player['AvgExitVel']/100, 
                       player['MaxDistance']/400,
                       player['HomeRuns']/10],
                    theta=['AVG', 'SLG', 'Exit Velo', 'Distance', 'HR'],
                    name=f"{player['Name']}"
                ))
            
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Top 5 Players by Exit Velocity'
            )
            
            # Create box plot
            velo_box = px.box(
                display_data,
                x='SkillLevel',
                y='MaxExitVel',
                points='all',
                title='Exit Velocity Distribution'
            )
            
            # Update filter options
            player_options = [{'label': name, 'value': name}
                            for name in sorted(stats_df['Name'].unique())]
            skill_options = [{'label': str(int(skill)), 'value': skill}
                           for skill in sorted(df['SkillLevel'].unique()) if pd.notna(skill)]

            return (
                display_data.to_dict('records'),
                columns,
                tooltip_data,
                scatter_fig,
                radar_fig, 
                velo_box,
                player_options,
                skill_options
            )
            
        except Exception as e:
            print(f"Error updating data: {str(e)}")
            empty_fig = px.scatter(title=f"Error: {str(e)}")
            return [], [], [], empty_fig, empty_fig, empty_fig, [], []

    @app.callback(
        [Output('summary-view', 'style'),
        Output('session-details-view', 'style'),
        Output('player-name-header', 'children'),
        Output('session-trend-graph', 'figure'),
        Output('session-heatmap', 'figure'),
        Output('session-metrics-chart', 'figure'),
        Output('session-details-table', 'data'),  # Changed from detailed-session-table
        Output('session-details-table', 'columns')],  # Changed from detailed-session-table
        [Input('hittrax-summary-table', 'active_cell'),
        Input('return-to-summary', 'n_clicks'),
        Input('session-date-filter', 'start_date'),
        Input('session-date-filter', 'end_date'),
        Input('session-stats-filter', 'value')]
    )
    def update_session_details(active_cell, return_clicks, start_date, end_date, selected_stats):
        ctx = callback_context
        if not ctx.triggered:
            return {'display': 'block'}, {'display': 'none'}, '', {}, {}, {}, [], []

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'return-to-summary':
            return {'display': 'block'}, {'display': 'none'}, '', {}, {}, {}, [], []
        
        if not active_cell:
            return {'display': 'block'}, {'display': 'none'}, '', {}, {}, {}, [], []
            
        try:
            # Get player data
            df = get_hittrax_data()
            player_name = df.iloc[active_cell['row']]['Name']
            player_data = get_player_details(player_name)
            
            # Apply date filters if selected
            if start_date and end_date:
                player_data = player_data[
                    (player_data['TimeStamp'] >= start_date) & 
                    (player_data['TimeStamp'] <= end_date)
                ]
            
            # Create trend graph
            trend_fig = px.line(
                player_data, 
                x='TimeStamp', 
                y=['AvgExitVel', 'MaxExitVel'],
                title='Exit Velocity Trends'
            )
            
            # Create heatmap
            heatmap_fig = px.density_heatmap(
                player_data,
                x='AvgExitVel',
                y='MaxDistance',
                title='Hit Distribution'
            )
            
            # Create metrics chart
            metrics_fig = px.line(
                player_data,
                x='TimeStamp',
                y=['AVG', 'SLG'],
                title='Batting Metrics Over Time'
            )
            
            # Create columns for detailed table
            columns = [
                {'name': 'TimeStamp', 'id': 'TimeStamp'},
                {'name': 'Name', 'id': 'Name'},
                {'name': 'MaxExitVel', 'id': 'MaxExitVel'},
                {'name': 'AvgExitVel', 'id': 'AvgExitVel'},
                {'name': 'MaxDistance', 'id': 'MaxDistance'},
                {'name': 'AvgDistance', 'id': 'AvgDistance'},
                {'name': 'AB', 'id': 'AB'},
                {'name': 'Hits', 'id': 'HitCount'},
                {'name': 'AVG', 'id': 'AVG'},
                {'name': 'SLG', 'id': 'SLG'},
                {'name': 'HomeRuns', 'id': 'HomeRuns'},
                {'name': 'Singles', 'id': 'Singles'},
                {'name': 'Doubles', 'id': 'Doubles'},
                {'name': 'Triples', 'id': 'Triples'},
                {'name': 'FoulBalls', 'id': 'FoulBalls'},
                {'name': 'Strikes', 'id': 'Strikes'},
                {'name': 'Balls', 'id': 'Balls'},
                {'name': 'LDPercentage', 'id': 'LDPercentage'},
                {'name': 'FBPercentage', 'id': 'FBPercentage'},
                {'name': 'HHVel', 'id': 'HHVel'},
                {'name': 'LOPercentage', 'id': 'LOPercentage'},
                {'name': 'MaxPoints', 'id': 'MaxPoints'},
                {'name': 'Score', 'id': 'Score'}
                # Add other columns as needed
            ]
            
            return (
                {'display': 'none'},  # Hide summary
                {'display': 'block'},  # Show details
                f"Session Details - {player_name}",
                trend_fig,
                heatmap_fig,
                metrics_fig,
                player_data.to_dict('records'),
                columns
            )
            
        except Exception as e:
            print(f"Error updating session details: {str(e)}")
            return {'display': 'block'}, {'display': 'none'}, '', {}, {}, {}, [], []

    return app

# In callbacks.py
def register_leaderboard_callbacks(app):
    @app.callback(
        [Output(f'leaderboard-content-max-exit-velocity', 'children'),
         Output(f'leaderboard-content-average-exit-velocity', 'children'),
         Output(f'leaderboard-content-max-distance', 'children'),
         Output(f'leaderboard-content-average-distance', 'children')],
        [Input('grad-year-tabs-max-exit-velocity', 'value'),
         Input('grad-year-tabs-average-exit-velocity', 'value'),
         Input('grad-year-tabs-max-distance', 'value'),
         Input('grad-year-tabs-average-distance', 'value'),
         Input('leaderboard-date-filter', 'start_date'),
         Input('leaderboard-date-filter', 'end_date')]
    )
    def update_all_leaderboards(max_exit_year, avg_exit_year, max_dist_year, 
                              avg_dist_year, start_date, end_date):
        try:
            data = get_leaderboard_data(start_date, end_date)
            if not data:
                return [html.Div("No data available")] * 4
            
            # Convert string years to integers for dictionary lookup
            metric_years = {
                'max-exit-velocity': int(max_exit_year or '2025'),
                'average-exit-velocity': int(avg_exit_year or '2025'),
                'max-distance': int(max_dist_year or '2025'),
                'average-distance': int(avg_dist_year or '2025')
            }
            
            results = []
            metrics = ['max-exit-velocity', 'average-exit-velocity', 
                      'max-distance', 'average-distance']
            
            for metric in metrics:
                metric_data = data.get(metric, {})
                selected_year = metric_years[metric]
                year_data = metric_data.get(selected_year, [])
                
                content = html.Div([
                    create_player_card(player_data) 
                    for player_data in year_data
                ]) if year_data else html.Div("No data available")
                
                results.append(content)
            
            return results
            
        except Exception as e:
            print(f"Error updating leaderboard content: {str(e)}")
            return [html.Div(f"Error loading leaderboard data: {str(e)}")] * 4
    
    return app

    # Add callback to ensure tab values stay in sync when needed
    @app.callback(
        [Output('grad-year-tabs-max-exit-velocity', 'value'),
         Output('grad-year-tabs-average-exit-velocity', 'value'),
         Output('grad-year-tabs-max-distance', 'value'),
         Output('grad-year-tabs-average-distance', 'value')],
        [Input('grad-year-tabs-max-exit-velocity', 'value'),
         Input('grad-year-tabs-average-exit-velocity', 'value'),
         Input('grad-year-tabs-max-distance', 'value'),
         Input('grad-year-tabs-average-distance', 'value')]
    )
    def sync_grad_years(max_exit_year, avg_exit_year, max_dist_year, avg_dist_year):
        ctx = callback_context
        if not ctx.triggered:
            return 2025, 2025, 2025, 2025
            
        # Get the input that triggered the callback
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        value = ctx.triggered[0]['value']
        
        # If "sync years" option is enabled, you could return the same value for all
        # For now, we'll just return each tab's own value
        return (max_exit_year or 2025, 
                avg_exit_year or 2025, 
                max_dist_year or 2025, 
                avg_dist_year or 2025)
    
    return app