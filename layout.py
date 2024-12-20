from dash import dcc, html
import dash_bootstrap_components as dbc

def create_layout():
    return dbc.Container([
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
