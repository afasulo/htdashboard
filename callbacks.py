from dash import html, dcc, callback_context
import dash
from dash.dependencies import Input, Output, State
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table
import pandas as pd
from sqlite_utils import get_hittrax_data, calculate_player_stats, get_player_details
from utils import COLUMN_FORMATS, COLUMN_GROUPS
from leaderboard_utils import get_leaderboard_data
from leaderboard_layout import create_player_card
from export_utils import create_leaderboard_pdf, create_social_media_image


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

            # Create scatter plot using the correct column names
            scatter_fig = px.scatter(
                display_data, 
                x='AvgExitVelMph',  # Updated column name 
                y='MaxDistanceFeet',  # Updated column name
                color='SkillLevel',
                size='AB',
                hover_data=['Name', 'AVG', 'SLG', 'HomeRuns', 'AB', 'HitCount'],
                text='Name',
                title='Exit Velocity vs Distance by Skill Level'
            )
            scatter_fig.update_traces(textposition='top center')
            
            # Create radar chart with the correct column names
            radar_fig = go.Figure()
            top_players = display_data.nlargest(5, 'AvgExitVelMph')  # Updated column name
            
            for _, player in top_players.iterrows():
                radar_fig.add_trace(go.Scatterpolar(
                    r=[player['AVG'], player['SLG'], 
                       player['AvgExitVelMph']/100,  # Updated column name 
                       player['MaxDistanceFeet']/400,  # Updated column name
                       player['HomeRuns']/10],
                    theta=['AVG', 'SLG', 'Exit Velo', 'Distance', 'HR'],
                    name=f"{player['Name']}"
                ))
            
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                showlegend=True,
                title='Top 5 Players by Exit Velocity'
            )
            
            # Create box plot with the correct column name
            velo_box = px.box(
                display_data,
                x='SkillLevel',
                y='MaxExitVelMph',  # Updated column name
                points='all',
                title='Exit Velocity Distribution'
            )
            
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
    return app

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

    @app.callback(
    [Output('export-status', 'children'),
     Output('export-data', 'data')],
    [Input('export-pdf-button', 'n_clicks'),
     Input('export-social-button', 'n_clicks')],
    [State('grad-year-tabs-max-exit-velocity', 'value'),
     State('leaderboard-date-filter', 'start_date'),
     State('leaderboard-date-filter', 'end_date')]  # Add date range states
)
    def handle_exports(pdf_clicks, social_clicks, grad_year, start_date, end_date):
        if not callback_context.triggered:
            return '', None
                
        trigger_id = callback_context.triggered[0]['prop_id'].split('.')[0]
        print(f"Export triggered: {trigger_id}")  # Debug print
        
        try:
            # Get leaderboard data with date range
            data = get_leaderboard_data(start_date, end_date)
            print("Leaderboard data structure:", data)  # Debug print
            
            if not data:
                print("No leaderboard data available")  # Debug print
                return "No data available for export", None
                    
            # Convert grad_year to int, handling string input
            grad_year = int(grad_year) if grad_year else 2025
            print(f"Grad year: {grad_year}")  # Debug print
                
            if trigger_id == 'export-pdf-button' and pdf_clicks:
                print("Generating PDF...")  # Debug print
                # Pass date range to PDF generation
                pdf_buffer = create_leaderboard_pdf(grad_year, data, start_date, end_date)
                
                # Convert to base64 for download
                pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                
                return "PDF generated successfully", {
                    'content': pdf_base64,
                    'filename': f'leaderboards_{grad_year}.pdf',
                    'type': 'application/pdf',
                    'base64': True
                }
                    
            elif trigger_id == 'export-social-button' and social_clicks:
                print("Generating social media image...")  # Debug print
                # Pass date range to image generation
                img_buffer = create_social_media_image(grad_year, data, start_date, end_date)
                
                # Convert to base64 for download
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                
                return "Image generated successfully", {
                    'content': img_base64,
                    'filename': f'leaderboards_{grad_year}.png',
                    'type': 'image/png',
                    'base64': True
                }
                    
        except Exception as e:
            print(f"Error during export: {str(e)}")  # Debug print
            import traceback
            traceback.print_exc()  # Print full error traceback
            return f"Error during export: {str(e)}", None
                
        return '', None

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
            return '2025', '2025', '2025', '2025'
            
        # Return string values for all years
        return (str(max_exit_year or '2025'), 
                str(avg_exit_year or '2025'), 
                str(max_dist_year or '2025'), 
                str(avg_dist_year or '2025'))

    return app