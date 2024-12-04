#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import plotly.express as px
from io import BytesIO
import base64
import dash_bootstrap_components as dbc
import os

# Initialize the app with a theme
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

# Layout
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("Hotel Calls Report Dashboard", className="text-center text-primary my-4"))),

    # File Upload Section
    dbc.Row([
        dbc.Col([
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select an Excel File')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=False
            ),
            html.Div(id='upload-status', className="text-center text-info my-2")
        ])
    ]),

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

    # Graphs Row with Loading Spinners
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="category-distribution"), type="circle"), width=12),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="calls-over-time"), type="circle"), width=12),
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
        }), width=6)
    ], className="mb-4")
])

# Global variable to store data
data = pd.DataFrame()

# Callbacks
@app.callback(
    [
        Output('upload-status', 'children'),
        Output('date-range-info', 'children'),
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    global data
    if contents is None:
        return "No file uploaded yet.", ""
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = pd.read_excel(BytesIO(decoded))
        data = data[['DATE', 'SERVICE CATEGORY', 'SERVICE- SUB CATEGORY', 'DESCRIPTION / RESOLUTION']].dropna()
        data['DATE'] = pd.to_datetime(data['DATE'])

        date_range_info = f"Data available from {data['DATE'].min().strftime('%Y-%m-%d')} to {data['DATE'].max().strftime('%Y-%m-%d')}"
        return f"File '{filename}' uploaded successfully!", date_range_info
    except Exception as e:
        return f"Error processing file: {str(e)}", ""


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
    []
)
def update_dashboard():
    global data
    if data.empty:
        return {}, {}, {}, html.Div("No data available"), "0", "0", "0", "0.0"

    # KPI Calculations
    total_calls = len(data)
    service_cat = data['SERVICE CATEGORY'].nunique()
    unique_issues = data['SERVICE- SUB CATEGORY'].nunique()
    daily_calls = data.groupby('DATE').size()
    avg_calls_day = round(daily_calls.mean(), 2)

    # Total Calls Over Time
    calls_over_time = data.groupby(data['DATE'].dt.to_period("D")).size().reset_index(name='Total Calls')
    calls_over_time['DATE'] = calls_over_time['DATE'].dt.to_timestamp()
    fig_calls_over_time = px.line(calls_over_time, x="DATE", y="Total Calls", title="Total Calls Over Time",
                                  markers=True, line_shape="spline", template="plotly_dark")
    fig_calls_over_time.update_layout(hovermode="x unified", title_x=0.5)

    # Service Category Distribution (Pie Chart)
    category_counts = data['SERVICE CATEGORY'].value_counts().reset_index()
    category_counts.columns = ['SERVICE CATEGORY', 'Count']
    fig_category_distribution = px.pie(category_counts, values="Count", names="SERVICE CATEGORY",
                                       title="Service Category Distribution", template="plotly_dark")
    fig_category_distribution.update_traces(textinfo="percent+label", pull=[0.05 for _ in category_counts['SERVICE CATEGORY']])

    # Sub-Service Category Bar Chart
    sub_category_counts = data['SERVICE- SUB CATEGORY'].value_counts().reset_index()
    sub_category_counts.columns = ['SERVICE- SUB CATEGORY', 'Count']
    fig_sub_category_bar = px.bar(sub_category_counts, x="SERVICE- SUB CATEGORY", y="Count",
                                  title="Sub-Service Categories", text="Count", template="plotly_dark")
    fig_sub_category_bar.update_traces(marker_color="royalblue")
    fig_sub_category_bar.update_layout(title_x=0.5)

    resolutions_list = html.Div("Click on a sub-category to see resolutions.")

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 if no port is specified
    app.run_server(host="0.0.0.0", port=port)
