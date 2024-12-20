from dash import Input, Output, State, html
import pandas as pd
import plotly.express as px
from process_data import process_file

def register_callbacks(app):
    @app.callback(
        [Output('upload-status', 'children'),
         Output('date-range-info', 'children'),
         Output('stored-data', 'data')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def handle_file_upload(contents, filename):
        if contents is None:
            return "No file uploaded yet.", "", None
        return process_file(contents, filename)

    @app.callback(
        [
            Output("calls-over-time", "figure"),
            Output("category-distribution", "figure"),
            Output("sub-category-bar", "figure"),
            Output("resolutions-list", "children"),
            Output("total-calls", "children"),
            Output("service_cat", "children"),
            Output("unique-issues", "children"),
            Output("avg-calls-day", "children"),
        ],
        [Input('stored-data', 'data')]
    )
    def update_dashboard(stored_data):
        if not stored_data:
            return {}, {}, {}, html.Div("No data available"), "0", "0", "0", "0.0"

        # Process data and return results
        df = pd.DataFrame(stored_data)
        total_calls = len(df)
        service_cat = df['SERVICE CATEGORY'].nunique()
        unique_issues = df['SERVICE- SUB CATEGORY'].nunique()
        daily_calls = df.groupby('DATE').size()
        avg_calls_day = round(daily_calls.mean(), 2)

        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        calls_over_time = df.groupby(df['DATE']).size().reset_index(name='Total Calls')

        fig_calls_over_time = px.line(calls_over_time, x="DATE", y="Total Calls", title="Total Calls Over Time")
        return (fig_calls_over_time, {}, {}, {}, str(total_calls), str(service_cat), str(unique_issues), f"{avg_calls_day:.2f}")
