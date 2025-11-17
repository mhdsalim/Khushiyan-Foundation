import dash
from dash import html
import dash_bootstrap_components as dbc
# from navbar import navbar
dash.register_page(__name__, path="/beach-cleanup")

# navbar = dbc.Navbar(
#     dbc.Container([
#         dbc.NavbarBrand("Khushiyaan Foundation Dashboard", className="ms-2",
#                         style={"fontWeight": "bold", "color": "white"}),

#         dbc.Nav(
#             [
#                 dbc.NavLink("Programme Impact", href="/programme-impact", active="exact"),
#                 dbc.NavLink("Beach Warriors Team", href="/beach-warriors-team", active="exact"),
#                 dbc.NavLink("Beach Cleanup", href="/beach-cleanup", active="exact"),
#                 dbc.NavLink("Waste Management", href="/waste-management", active="exact"),
#             ],
#             pills=True
#         )
#     ]),
#     color="dark",
#     dark=True,
#     style={"padding": "10px"}
# )

layout = html.Div([
    # navbar,
    html.H2("Beach Cleanup", style={"marginTop": "20px", "textAlign": "center"}),
    html.P("Coming Soon...", style={"fontSize": "18px", "textAlign": "center"})
], style={"padding": "0 0 50px 0"})
