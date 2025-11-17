import dash
from dash import html, dcc, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import re
import os
from flask_login import login_user
from auth import User   # import shared User class
from dotenv import load_dotenv

env_path = r"C:\Users\Alisha Khan\Khushiyaan-Foundation-Dashboard\.env"
load_dotenv(dotenv_path=env_path)


# Admin
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_CLIENT = os.getenv("ADMIN_CLIENT")

# Viewer
VIEWER_USERNAME = os.getenv("VIEWER_USERNAME")
VIEWER_PASSWORD = os.getenv("VIEWER_PASSWORD")
VIEWER_CLIENT = os.getenv("VIEWER_CLIENT")

# HCL
HCL_USERNAME = os.getenv("HCL_USERNAME")
HCL_PASSWORD = os.getenv("HCL_PASSWORD")
HCL_CLIENT = os.getenv("HCL_CLIENT")

# KHF
KHF_USERNAME = os.getenv("KHF_USERNAME")
KHF_PASSWORD = os.getenv("KHF_PASSWORD")
KHF_CLIENT = os.getenv("KHF_CLIENT")

# Store in USERS dictionary
USERS = {
    ADMIN_USERNAME: {"password": ADMIN_PASSWORD, "client": ADMIN_CLIENT},
    VIEWER_USERNAME: {"password": VIEWER_PASSWORD, "client": VIEWER_CLIENT},
    HCL_USERNAME: {"password": HCL_PASSWORD, "client": HCL_CLIENT},
    KHF_USERNAME: {"password": KHF_PASSWORD, "client": KHF_CLIENT},
}

# Register page
dash.register_page(__name__, path="/", title="Login")

# Layout - this MUST be a variable named 'layout'
layout = html.Div(
    className="login-page",
    children=[
        # 🔗 Header container (Logo + Social Icons)
        html.Div(
            children=[
                # Logo
                html.Img(
                    src="/assets/Khushiyaan Logo.jpg",
                    style={
                        "height": "50px",
                        "marginRight": "15px"
                    }
                ),
                # Social Icons
                html.Div(
                    children=[
                        html.A(
                            html.I(className="fab fa-facebook-f"),
                            href="https://www.facebook.com/khushiyaanorg?mibextid=ZbWKwL",
                            target="_blank",
                            style={
                                "margin": "0 6px",
                                "color": "#FFD700",        # gold/yellow icons
                                "fontSize": "16px",
                                "backgroundColor": "#0c1b36",  # navy blue circle
                                "borderRadius": "50%",
                                "padding": "10px",
                                "display": "inline-flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "width": "36px",
                                "height": "36px",
                                "textAlign": "center",
                            }
                        ),
                        html.A(
                            html.I(className="fab fa-twitter"),
                            href="https://www.facebook.com/khushiyaanorg?mibextid=ZbWKwL",
                            target="_blank",
                            style={
                                "margin": "0 6px",
                                "color": "#FFD700",
                                "fontSize": "16px",
                                "backgroundColor": "#0c1b36",
                                "borderRadius": "50%",
                                "padding": "10px",
                                "display": "inline-flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "width": "36px",
                                "height": "36px",
                                "textAlign": "center",
                            }
                        ),
                        html.A(
                            html.I(className="fab fa-instagram"),
                            href="https://www.instagram.com/khushiyaanorg?igshid=NTc4MTIwNjQ2YQ%3D%3D",
                            target="_blank",
                            style={
                                "margin": "0 6px",
                                "color": "#FFD700",
                                "fontSize": "16px",
                                "backgroundColor": "#0c1b36",
                                "borderRadius": "50%",
                                "padding": "10px",
                                "display": "inline-flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "width": "36px",
                                "height": "36px",
                                "textAlign": "center",
                            }
                        ),
                        html.A(
                            html.I(className="fab fa-linkedin in"),
                            href="https://www.linkedin.com/company/khushiyaan-foundation/posts/?feedView=all",
                            target="_blank",
                            style={
                                "margin": "0 6px",
                                "color": "#FFD700",
                                "fontSize": "16px",
                                "backgroundColor": "#0c1b36",
                                "borderRadius": "50%",
                                "padding": "10px",
                                "display": "inline-flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "width": "36px",
                                "height": "36px",
                                "textAlign": "center",
                            }
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"}
                )
            ],
            style={
                "position": "absolute",
                "top": "15px",
                "left": "20px",
                "display": "flex",
                "alignItems": "center"
            }
        ),

        
        # dcc.Store(id="session", storage_type="session"),
        html.Div(
            className="login-box",
            children=[
                html.H3(
                    "Welcome to India's First Coastal Cleanup & Waste Management Dashboard",
                    style={
                        "textAlign": "center",
                        "marginBottom": "20px",
                        "fontSize": "clamp(16px, 4vw, 20px)",
                        "lineHeight": "1.4",
                        "whiteSpace": "pre-line",
                        "fontWeight": "bold",
                        "color": "#003366"
                    }
                ),
                dbc.Input(
                    id="username", placeholder="Username",
                    type="text",
                    className="mb-3",
                    style={"fontSize": "16px", "padding": "10px"}
                ),
                dbc.Input(
                    id="password", placeholder="Password",
                    type="password",
                    className="mb-3",
                    style={"fontSize": "16px", "padding": "10px"}
                ),
                dbc.Button(
                    "Login", id="login-button",
                    color="primary",
                    className="mb-2 w-100",
                    style={"fontSize": "16px", "padding": "10px"}
                ),
                html.Div(
                    id="login-output",
                    style={
                        "color": "red",
                        "marginTop": "10px",
                        "textAlign": "center",
                        "fontSize": "14px"
                    }
                ),
                dcc.Location(id="url", refresh=True)
                
            ]
        ),
        html.Footer(
            className="footer-stats",
            children=[
                html.Div(
                    className="stat-card",
                    children=[
                        html.H3("189,290", id="participants-count", className="stat-number"),
                        html.P("People Participated", className="stat-label"),
                    ]
                ),
                html.Div(
                    className="stat-card",
                    children=[
                        html.H3("1300+", id="waste-count", className="stat-number"),
                        html.P("Number of Beach Cleanups", className="stat-label"),
                    ]
                ),
                html.Div(
                    className="stat-card",
                    children=[
                        html.H3("2.3M+ Kg", id="recycle-count", className="stat-number"),
                        html.P("Marine Debris Collected", className="stat-label"),
                    ]
                ),
            ]
        )
    ]
)

# Login callback
@callback(
    Output("login-output", "children"),
    Output("url", "pathname"),
    Input("login-button", "n_clicks"),
    Input("username", "n_submit"),
    Input("password", "n_submit"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def validate_login(btn_clicks, username_submit, password_submit, username, password):
    # Triggered if login button clicked OR Enter pressed
    if btn_clicks or username_submit or password_submit:
        if not username or not password:
            return "⚠️ Please enter both username and password.", no_update

        # 🔑 Check against USERS dictionary
        user_info = USERS.get(username)
        if user_info and user_info["password"] == password:
            user = User(id=username)
            login_user(user, remember=True)

            # Store client in Flask session for filtering later
            import flask
            flask.session["client"] = user_info["client"]

            return "", "/programme-impact"

        # ❌ Invalid credentials
        return "❌ Invalid username or password.", no_update

    return "", no_update