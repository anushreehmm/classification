from dash import Dash
import dash_bootstrap_components as dbc
from layout import create_layout
from callbacks import register_callbacks

app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
app.title = "Hotel Calls Report Dashboard"

# Set the app layout
app.layout = create_layout()

# Register all callbacks
register_callbacks(app)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
