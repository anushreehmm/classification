import pandas as pd
from dash import Input, Output, State, html, dcc
from process_data import process_uploaded_file, create_figures

def register_callbacks(app):
    @app.callback(
        [Output('upload-status', 'children'),
         Output('date-range-info', 'children'),
         Output('stored-data', 'data')],
        Input('upload-data', 'contents'),
        State('upload-data', 'filename')
    )
    def handle_file_upload(contents, filename):
        return process_uploaded_file(contents, filename)

    @app.callback(
        [Output("calls-over-time", "figure"),
         Output("category-distribution", "figure"),
         Output("sub-category-bar", "figure"),
         Output("resolutions-list", "children"),
         Output("total-calls", "children"),
         Output("service_cat", "children"),
         Output("unique-issues", "children"),
         Output("avg-calls-day", "children")],
        [Input('stored-data', 'data'),
         Input("category-distribution", "clickData"),
         Input("sub-category-bar", "clickData")]
    )
    def update_dashboard(stored_data, category_click_data, sub_category_click_data):
        return create_figures(stored_data, category_click_data, sub_category_click_data)
