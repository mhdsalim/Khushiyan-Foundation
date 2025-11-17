# import dash_bootstrap_components as dbc
# from dash import html

# navbar = dbc.Navbar(
#     dbc.Container([
#         dbc.NavbarBrand(
#             "Khushiyaan Foundation Dashboard",
#             className="ms-2",
#             style={"fontWeight": "bold", "color": "white"}
#         ),
#         dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
#         dbc.Collapse(
#             dbc.Nav(
#                 [
#                     dbc.NavLink("Programme Impact", href="/programme-impact", active="exact", className="me-2"),
#                     dbc.NavLink("Beach Warriors Team", href="/beach-warriors-team", active="exact", className="me-2"),
#                     dbc.NavLink("Beach Cleanup", href="/beach-cleanup", active="exact", className="me-2"),
#                     dbc.NavLink("Waste Management", href="/waste-management", active="exact", className="me-2")
#                 ],
#                 pills=True,
#                 navbar=True,
#                 className="ms-auto"
#             ),
#             id="navbar-collapse",
#             is_open=False,
#             navbar=True,
#         ),
#     ], fluid=True),
#     color="dark",
#     dark=True,
#     style={"padding": "10px", "position": "sticky", "top": 0, "zIndex": 1000, "width": "100%"}
# )

# from dash import callback, Output, Input

# @callback(
#     Output("navbar-collapse", "is_open"),
#     Input("navbar-toggler", "n_clicks"),
#     prevent_initial_call=True
# )
# def toggle_navbar(n):
#     return n % 2 == 1