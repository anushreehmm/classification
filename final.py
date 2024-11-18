#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, ctx
import plotly.express as px
from wordcloud import WordCloud
import base64
from io import BytesIO
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

    # Filters Row
    dbc.Row([
        dbc.Col([
            html.Label("Select Service Category:", className="fw-bold"),
            dcc.Dropdown(
                id='category-dropdown',
                placeholder="Select a category",
                multi=True,
                style={'color': '#000'}
            )
        ], width=6),
    ], className="my-4"),

    # KPIs Row
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Total Calls", className="card-title"),
                html.H3(id="total-calls", className="text-info")
            ])
        ], className="shadow-sm"), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Unique Issues", className="card-title"),
                html.H3(id="unique-issues", className="text-info")
            ])
        ], className="shadow-sm"), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Average Calls per Day", className="card-title"),
                html.H3(id="avg-calls-day", className="text-info")
            ])
        ], className="shadow-sm"), width=4),
    ], className="my-4"),

    # Graphs Row with Loading Spinners
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="calls-over-time"), type="circle"), width=6),
        dbc.Col(dcc.Loading(dcc.Graph(id="category-distribution"), type="circle"), width=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="sub-category-bar"), type="circle"), width=6),
        dbc.Col(dcc.Loading(html.Div(id='word-cloud', style={'text-align': 'center'}), type="circle"), width=6),
    ]),
], fluid=True)

# Global variable to store data
data = pd.DataFrame()

# Callbacks
@app.callback(
    [
        Output('upload-status', 'children'),
        Output('date-range-info', 'children'),
        Output('category-dropdown', 'options'),
        Output('category-dropdown', 'value')
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_file_upload(contents, filename):
    global data
    if contents is None:
        return "No file uploaded yet.", "", [], None
    
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        data = pd.read_excel(BytesIO(decoded))
        data = data[['DATE', 'SERVICE CATEGORY', 'SERVICE- SUB CATEGORY', 'DESCRIPTION / RESOLUTION']].dropna()
        data['DATE'] = pd.to_datetime(data['DATE'])

        date_range_info = f"Data available from {data['DATE'].min().strftime('%Y-%m-%d')} to {data['DATE'].max().strftime('%Y-%m-%d')}"
        category_options = [{'label': 'All', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in data['SERVICE CATEGORY'].unique()]

        return f"File '{filename}' uploaded successfully!", date_range_info, category_options, None
    except Exception as e:
        return f"Error processing file: {str(e)}", "", [], None


@app.callback(
    [
        Output("calls-over-time", "figure"),
        Output("category-distribution", "figure"),
        Output("sub-category-bar", "figure"),
        Output("word-cloud", "children"),
        Output("total-calls", "children"),
        Output("unique-issues", "children"),
        Output("avg-calls-day", "children"),
    ],
    [Input("category-dropdown", "value"),
     Input("category-distribution", "clickData")]
)
def update_dashboard(selected_categories, click_data):
    global data
    if data.empty:
        return {}, {}, {}, html.Div("No data available"), "", "", ""
    
    # Filter data based on selection
    if not selected_categories or "All" in selected_categories:
        filtered_data = data
    else:
        filtered_data = data[data['SERVICE CATEGORY'].isin(selected_categories)]

    # KPI Calculations
    total_calls = len(filtered_data)
    unique_issues = filtered_data['SERVICE- SUB CATEGORY'].nunique()
    avg_calls_day = round(total_calls / ((data['DATE'].max() - data['DATE'].min()).days + 1), 2)

    # Total Calls Over Time
    calls_over_time = filtered_data.groupby(filtered_data['DATE'].dt.to_period("D")).size().reset_index(name='Total Calls')
    calls_over_time['DATE'] = calls_over_time['DATE'].dt.to_timestamp()
    fig_calls_over_time = px.line(calls_over_time, x="DATE", y="Total Calls", title="Total Calls Over Time",
                                  markers=True, line_shape="spline", template="plotly_dark")
    fig_calls_over_time.update_layout(hovermode="x unified", title_x=0.5)

    # Service Category Distribution (Pie Chart)
    category_counts = filtered_data['SERVICE CATEGORY'].value_counts().reset_index()
    category_counts.columns = ['SERVICE CATEGORY', 'Count']
    fig_category_distribution = px.pie(category_counts, values="Count", names="SERVICE CATEGORY",
                                       title="Service Category Distribution", template="plotly_dark")
    fig_category_distribution.update_traces(textinfo="percent+label", pull=[0.05 for _ in category_counts['SERVICE CATEGORY']])

    # Sub-Service Category (Dynamic Bar Chart)
    if click_data:
        selected_service_category = click_data['points'][0]['label']
        sub_category_data = filtered_data[filtered_data['SERVICE CATEGORY'] == selected_service_category]
    else:
        sub_category_data = filtered_data

    sub_category_counts = sub_category_data['SERVICE- SUB CATEGORY'].value_counts().reset_index()
    sub_category_counts.columns = ['SERVICE- SUB CATEGORY', 'Count']
    fig_sub_category_bar = px.bar(sub_category_counts, x="SERVICE- SUB CATEGORY", y="Count",
                                  title="Sub-Service Categories", text="Count", template="plotly_dark")
    fig_sub_category_bar.update_traces(marker_color="royalblue")
    fig_sub_category_bar.update_layout(title_x=0.5)

    # Word Cloud for Description / Resolution
    wordcloud = WordCloud(width=800, height=400, background_color="black", colormap='coolwarm').generate(
        " ".join(filtered_data['DESCRIPTION / RESOLUTION']))
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    word_cloud_img = base64.b64encode(img.getvalue()).decode()
    word_cloud_element = html.Img(src="data:image/png;base64,{}".format(word_cloud_img), 
                                  style={'width': '100%', 'border-radius': '10px'})

    return (
        fig_calls_over_time,
        fig_category_distribution,
        fig_sub_category_bar,
        word_cloud_element,
        total_calls,
        unique_issues,
        avg_calls_day,
    )


# Run the app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))  # Default to 8050 if no port is specified
    app.run_server(host="0.0.0.0", port=port)



# In[ ]:




