import dash
import os
from dash import html, dcc
import dash_bootstrap_components as dbc
from auth import login_manager 
from dotenv import load_dotenv
from utils.scheduler import start_scheduler
load_dotenv()  # import shared login_manager
# Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server
@server.route("/trigger-certificates", methods=["POST"])
def trigger_certificates():
    data = request.json or {}

    # Security check
    if data.get("secret") != os.getenv("WEBHOOK_SECRET"):
        return jsonify({"error": "Unauthorized"}), 403

    row_values = data.get("values")  # ["Salim", "salim@gmail.com", "Cleanup", "2025-10-13"]

    if not row_values:
        return jsonify({"error": "Missing row data"}), 400

    # Example: Extract fields
    name, event,date_str ,location, sponsor, photo_path, email = row_values[1:8]
    row  = data.get("row")

    # Generate + send certificate for this one row
    status = send_single_certificate(name, email,event,date_str ,location, sponsor, photo_path,row)

    return jsonify({"status": "ok", "sent_to": email, "result": status})

# IMPORTANT: Set secret key for Flask sessions
server.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
print(server.secret_key)

# Initialize login manager with Flask server
login_manager.init_app(server)
login_manager.login_view = "/"   # redirect to login if not logged in

# Main layout
app.layout = html.Div([
    dcc.Store(id="screen-width"),
    dcc.Interval(id="interval", interval=10000, n_intervals=0),
    dash.page_container
])

# Clientside callback to track screen width
app.clientside_callback(
    """
    function(n_intervals) {
        return window.innerWidth;
    }
    """,
    dash.Output("screen-width", "data"),
    dash.Input("interval", "n_intervals")
)
start_scheduler()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)

