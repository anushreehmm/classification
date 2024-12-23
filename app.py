from dash import Dash
import dash_bootstrap_components as dbc
from layout import app_layout
from callbacks import register_callbacks

# Initialize the Dash app with a Bootstrap theme
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

# Set the app layout
app.layout = app_layout

# Register the callbacks
register_callbacks(app)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
