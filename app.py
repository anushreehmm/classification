#!/usr/bin/env python
# coding: utf-8
 
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc
from io import BytesIO
import base64
import os
 
# Initialize the app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
 
# Define the app layout
app.layout = dbc.Container([
    # Title
    dbc.Row(dbc.Col(html.H1("Hotel Calls Report Dashboard", className="text-center text-primary my-4"))),
 
    # File Upload Section
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.Button(
                        'Upload Excel File',
                        id='upload-button',
                        style={
                            'padding': '15px 30px',
                            'fontSize': '16px',
                            'color': '#fff',
                            'backgroundColor': '#007bff',
                            'border': 'none',
                            'borderRadius': '8px',
                            'cursor': 'pointer',
                            'transition': 'all 0.3s ease-in-out'
                        }
                    )
                ]),
                style={
                    'display': 'flex',
                    'justifyContent': 'center',
                    'alignItems': 'center',
                    'margin': '20px',
                    'textAlign': 'center'
                },
                multiple=False
            ),
            html.Div(id='upload-status', className="text-center text-info my-2")
        ])
    ]),
 
    # Store to hold uploaded data
dcc.Store(id='stored-data', storage_type='memory'),
 
    # Displaying Date Range Information
    dbc.Row([
        dbc.Col(html.Div(id='date-range-info', className="text-center text-secondary fw-bold"), width=12)
    ], className="mb-4"),
 
    # KPIs Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Calls", className="card-title"),
                html.H3(id="total-calls", className="text-info")
            ])
        ], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Service Categories", className="card-title"),
                html.H3(id="service_cat", className="text-info")
            ])
        ], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Sub-Service Categories", className="card-title"),
                html.H3(id="unique-issues", className="text-info")
            ])
        ], className="shadow-sm"), width=3),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Calls per Day", className="card-title"),
                html.H3(id="avg-calls-day", className="text-info")
            ])
        ], className="shadow-sm"), width=3),
    ], className="my-4"),
 
    # Graphs Section
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="calls-over-time"), type="circle"), width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="category-distribution"), type="circle"), width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="sub-category-bar"), type="circle"), width=6),
        dbc.Col(html.Div(id='resolutions-list', style={
            'border': '1px solid #ccc',
            'padding': '15px',
            'border-radius': '10px',
            'height': '400px',
            'overflow-y': 'scroll',
            'background-color': '#f8f9fa',
            'color': '#212529'
        }), width=6),
    ], className="mb-4")
])
 
# Callback to process uploaded file and store data
@app.callback(
    [
        Output('upload-status', 'children'),
        Output('date-range-info', 'children'),
        Output('stored-data', 'data')
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    if contents is None:
        return "No file uploaded yet.", "", None
 
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_excel(BytesIO(decoded))
        df = df[['DATE', 'SERVICE CATEGORY', 'SERVICE- SUB CATEGORY', 'DESCRIPTION / RESOLUTION']].dropna()
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df = df[df['DATE'].dt.year >= 2024]
 
        if df.empty:
            return f"No valid data from 2024 in '{filename}'. Please upload a suitable file.", "", None
 
        date_range_info = f"Data available from {df['DATE'].min().strftime('%Y-%m-%d')} to {df['DATE'].max().strftime('%Y-%m-%d')}"
        return f"File '{filename}' uploaded successfully!", date_range_info, df.to_dict('records')
    except Exception as e:
        return f"Error processing file: {str(e)}", "", None
 
# Callback to update graphs and KPIs
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
    [Input('stored-data', 'data'), Input("category-distribution", "clickData"), Input("sub-category-bar", "clickData")]
)
def update_dashboard(stored_data, category_click_data, sub_category_click_data):
    if not stored_data:
        return {}, {}, {}, html.Div("No data available"), "0", "0", "0", "0.0"
 
    df = pd.DataFrame(stored_data)
    total_calls = len(df)
    service_cat = df['SERVICE CATEGORY'].nunique()
    unique_issues = df['SERVICE- SUB CATEGORY'].nunique()
    daily_calls = df.groupby('DATE').size()
    avg_calls_day = round(daily_calls.mean(), 2)
 
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    calls_over_time = df.groupby(df['DATE'].dt.to_period("D")).size().reset_index(name='Total Calls')
    calls_over_time['DATE'] = calls_over_time['DATE'].dt.to_timestamp()
    fig_calls_over_time = px.line(calls_over_time, x="DATE", y="Total Calls", title="Total Calls Over Time",
                                  markers=True, line_shape="spline", template="plotly_dark")
    fig_calls_over_time.update_layout(hovermode="x unified", title_x=0.5)
 
    category_counts = df['SERVICE CATEGORY'].value_counts().reset_index()
    category_counts.columns = ['SERVICE CATEGORY', 'Count']
    fig_category_distribution = px.pie(category_counts, values="Count", names="SERVICE CATEGORY",
                                       title="Service Category Distribution", template="plotly_dark")
    fig_category_distribution.update_traces(textinfo="percent+label", pull=[0.05] * len(category_counts))
 
    # Handle category clickData to filter sub-category bar chart
    if category_click_data and "points" in category_click_data:
        clicked_category = category_click_data["points"][0]["label"]
        filtered_df = df[df['SERVICE CATEGORY'] == clicked_category]
    else:
        filtered_df = df
 
    sub_category_counts = filtered_df['SERVICE- SUB CATEGORY'].value_counts().reset_index()
    sub_category_counts.columns = ['SERVICE- SUB CATEGORY', 'Count']
    fig_sub_category_bar = px.bar(sub_category_counts, x="SERVICE- SUB CATEGORY", y="Count",
                                  title="Sub-Service Categories", text="Count", template="plotly_dark")
    fig_sub_category_bar.update_traces(marker_color="royalblue")
    fig_sub_category_bar.update_layout(title_x=0.5)
 
    # Handle sub-category clickData to filter resolutions
    if sub_category_click_data and "points" in sub_category_click_data:
        clicked_sub_category = sub_category_click_data["points"][0]["label"]
        resolutions_df = filtered_df[filtered_df['SERVICE- SUB CATEGORY'] == clicked_sub_category]
    else:
        resolutions_df = filtered_df
 
    resolutions_list = html.Ul([html.Li(resolution) for resolution in resolutions_df['DESCRIPTION / RESOLUTION'].unique()])
 
    return (
        fig_calls_over_time,
        fig_category_distribution,
        fig_sub_category_bar,
        resolutions_list,
        str(total_calls),
        str(service_cat),
        str(unique_issues),
        f"{avg_calls_day:.2f}",
    )
 
# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
