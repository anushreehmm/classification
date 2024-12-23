import base64
import pandas as pd
from io import BytesIO
import plotly.express as px
from dash import html

def process_uploaded_file(contents, filename):
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

def create_figures(stored_data, category_click_data, sub_category_click_data):
    if not stored_data:
        return {}, {}, {}, html.Div("No data available"), "0", "0", "0", "0.0"

    df = pd.DataFrame(stored_data)
    total_calls = len(df)
    service_cat = df['SERVICE CATEGORY'].nunique()
    unique_issues = df['SERVICE- SUB CATEGORY'].nunique()
    avg_calls_day = df.groupby('DATE').size().mean()

    calls_over_time = df.groupby(df['DATE'].dt.to_period("D")).size().reset_index(name='Total Calls')
    calls_over_time['DATE'] = calls_over_time['DATE'].dt.to_timestamp()
    fig_calls_over_time = px.line(calls_over_time, x="DATE", y="Total Calls", title="Total Calls Over Time",
                                  markers=True, template="plotly_dark")

    category_counts = df['SERVICE CATEGORY'].value_counts().reset_index()
    fig_category_distribution = px.pie(category_counts, values='SERVICE CATEGORY', names='index', title="Category Distribution")

    if category_click_data:
        clicked_category = category_click_data["points"][0]["label"]
        df = df[df['SERVICE CATEGORY'] == clicked_category]

    sub_category_counts = df['SERVICE- SUB CATEGORY'].value_counts()
    fig_sub_category_bar = px.bar(sub_category_counts, x=sub_category_counts.index, y=sub_category_counts.values,
                                  title="Sub-Service Categories")

    resolutions = [html.Li(resolution) for resolution in df['DESCRIPTION / RESOLUTION'].unique()]
    return fig_calls_over_time, fig_category_distribution, fig_sub_category_bar, resolutions, str(total_calls), str(service_cat), str(unique_issues), f"{avg_calls_day:.2f}"
