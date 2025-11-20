import dash
from dash import html, dcc, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from dash import dash_table
from flask import session
# from navbar import navbar
from flask_login import current_user, logout_user  # Added Flask-Login imports
# import plotly.io as pio
import plotly.io as pio
from utils.google_sheet import fetch_form_responses,format_pretty_date,update_sheet
from utils.certificate_generator import generate_certificate
from utils.mailer import send_certificate_mail,create_smtp_client
import time

# 🎨 Khushiyaan Foundation Brand Palette
khushiyaan_colors = ["#001F54", "#FFD300", "#808080", "#008080", "#B0B0B0"]

pio.templates["khushiyaan"] = pio.templates["plotly"].update({
    "layout": {
        "colorway": khushiyaan_colors
    }
})

pio.templates.default = "khushiyaan"

dash.register_page(__name__, path="/programme-impact")

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "final_dataframe1.csv")
df = pd.read_csv(DATA_FILE)



df.columns = [c.strip().replace("\t", "").replace("\n","")
for c in df.columns]
for col in df.columns:
    if col not in ["Year Period", "location", "client"]:
        df[col]=pd.to_numeric(df[col],
        errors="coerce")

# Get available year periods and locations for dropdowns
available_year_periods = sorted(df["Year Period"].unique()) if "Year Period" in df.columns else []
available_locations = sorted(df["location"].unique()) if "location" in df.columns else []

def get_filtered_df():
    client = session.get("client", "all")  
    
    if client.lower() == "all":   # admin sees everything
        return df.copy()
    else:                 # specific client sees only their data
        return df[df["client"].str.strip().str.lower() == client.strip().lower()].copy()

def short_label(col):
    """Extract the last part of column name after underscore"""
    try:
        return col.split("_")[-1]
    except Exception:
        return col

def get_columns_by_prefix(df, prefix):
    """Return all columns that start with given prefix"""
    return [col for col in df.columns if col.startswith(prefix)]

def no_data_fig(message="No data for selected range"):
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5,
                       showarrow=False, font=dict(size=16, color="red"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(height=350)
    return fig

def kpi_card(title, value, gradient):
    return dbc.Card(
        dbc.CardBody([
            html.H4(f"{value:,.0f}", className="card-title",
                    style={"color": "white", "fontWeight": "bold", "marginBottom": "8px", "fontSize": "22px"}),
            html.P(title, className="card-text", style={"color": "white", "margin": 0, "fontSize": "14px"})
        ],
            style={"display": "flex", "flexDirection": "column", "justifyContent": "center",
                   "alignItems": "center", "height": "130px"}
        ),
        style={"background": gradient, "borderRadius": "12px", "boxShadow": "0 4px 10px rgba(0,0,0,0.12)",
               "textAlign": "center"}
    )

def dual_axis_component(section_id, y1_default, y2_default, options):
    opts = [{"label": short_label(col), "value": col} for col in options]
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.Label("Y1:", style={"fontSize": 12, "fontWeight": "600"}),
                dcc.Dropdown(id={"type": "y1", "section": section_id}, options=opts, value=y1_default,
                             clearable=False)
            ], width=6),
            dbc.Col([
                html.Label("Y2:", style={"fontSize": 12, "fontWeight": "600"}),
                dcc.Dropdown(id={"type": "y2", "section": section_id}, options=opts, value=y2_default,
                             clearable=False)
            ], width=6)
        ], style={"marginBottom": "8px"}),
        dcc.Graph(id={"type": "dual-axis-graph", "section": section_id},
                  style={"height": "350px", "width": "100%"},
                  className="graph-figure",
                  config={"responsive": True})
    ])

Y1_COLOR = khushiyaan_colors[0]
Y2_COLOR = khushiyaan_colors[1]
gradients = [
    "linear-gradient(135deg, #001F54, #001F54)",
    "linear-gradient(135deg, #FFD300, #FFD300)",
    "linear-gradient(135deg, #808080, #808080)",
    "linear-gradient(135deg, #008080, #008080)"
]

# ---------------- Sections Config ----------------
sections_config = []

# 1. Beach Clean Up
beach_cols = get_columns_by_prefix(df, "Beach Clean Up_")
# Add waste management columns that are relevant to beach clean up
beach_waste_cols = [col for col in get_columns_by_prefix(df, "Waste Management_") 
                   if "Debris" in col or "Total Waste" in col]
beach_cols = beach_cols + beach_waste_cols[:1] if beach_waste_cols else beach_cols

def beach_graph2(dff, screen_width=None):
    # Get participant-related columns from beach clean up
    participant_cols = [col for col in get_columns_by_prefix(dff, "Beach Clean Up_") 
                       if "Participants" in col or "Volunteers" in col or "Representatives" in col]
    cols = participant_cols[:5] if len(participant_cols) >= 5 else participant_cols
    
    if not cols or dff.empty:
        return no_data_fig("No participant data available")
        
    # Calculate sums and handle NaN values
    vals = dff[cols].fillna(0).sum().values
    # Filter out zero values for cleaner pie chart
    non_zero_mask = vals > 0
    if not non_zero_mask.any():
        return no_data_fig("No participant data available")
    
    vals = vals[non_zero_mask]
    names = [short_label(c) for i, c in enumerate(cols) if non_zero_mask[i]]
    # fig = px.pie(values=vals, names=names, hole=0.5, title="Participant Distribution Accross Categories")
    fig = px.pie(values=vals, names=names, hole=0.5, title="Participant Distribution Accross Categories")
    fig.update_traces(textposition="inside", textinfo="percent")   # ✅ add this line

   
    if screen_width and screen_width < 768:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=40, b=120, l=20, r=20),
            height=400
        )
    else:
        fig.update_layout(
            legend=dict(orientation="v", y=0.5, yanchor="middle", x=1.02, xanchor="left"),
            margin=dict(t=40, b=40, l=40, r=20),
            height=350
        )

    fig.update_layout(
        title=dict(y=1.0, x=0.5, xanchor="center")
    )
    fig.update_traces(domain=dict(y=[0.15, 0.85]))
    return fig

sections_config.append({
    "id": "beach",
    "title": "🏖 Beach Clean Up",
    "kpi_cols": beach_cols[:4] if len(beach_cols) >= 4 else beach_cols,
    "graph1_defaults": [beach_cols[0], beach_cols[1]] if len(beach_cols) >= 2 else beach_cols,
    "graph1_opts": beach_cols,
    "graph2_fn": beach_graph2
})

 
# 2. Waste Management
waste_cols = get_columns_by_prefix(df, "Waste Management_")

def waste_graph2(dff, screen_width):
    if dff.empty:
        return no_data_fig()
    
    # Find waste collection related columns
    collection_cols = [col for col in get_columns_by_prefix(dff, "Waste Management_") 
                      if "Collected" in col or "Debris" in col]
    
    if len(collection_cols) >= 2:
        col_map = {collection_cols[0]: short_label(collection_cols[0]), 
                  collection_cols[1]: short_label(collection_cols[1])}
    elif len(collection_cols) == 1:
        col_map = {collection_cols[0]: short_label(collection_cols[0])}
    else:
        return no_data_fig("No waste collection data available")
    
    # Create a clean dataframe for plotting
    plot_data = dff[["Year Period"] + list(col_map.keys())].copy()
    
    # Fill NaN values with 0
    for col in col_map.keys():
        plot_data[col] = plot_data[col].fillna(0)
    
    # Rename columns for display
    plot_data = plot_data.rename(columns=col_map)
    
    # Check if we have any meaningful data
    data_cols = list(col_map.values())
    if plot_data[data_cols].sum().sum() <= 0:
        return no_data_fig("No waste collection data available")
    
    fig = px.bar(plot_data, x="Year Period", y=data_cols, barmode="stack", 
                title="Waste Collection Metrics", labels={v: v for v in col_map.values()})

    if screen_width and screen_width < 768:
        fig.update_layout(
            height=350,
            legend=dict(
                orientation="h",
                y=-0.18,
                x=0.5,
                xanchor="center",
                yanchor="top"
            ),
            margin=dict(t=60, b=100, l=40, r=20)
        )
    else:
        fig.update_layout(
            height=500,  
            legend=dict(
                orientation="h",
                y=-0.18,
                x=0.5,
                xanchor="center",
                yanchor="top"
            ),
            margin=dict(t=60, b=80, l=40, r=20)
        )
    return fig

sections_config.append({
    "id": "waste",
    "title": "♻ Waste Management",
    "kpi_cols": waste_cols[:4] if len(waste_cols) >= 4 else waste_cols,
    "graph1_defaults": [waste_cols[0], waste_cols[1]] if len(waste_cols) >= 2 else waste_cols,
    "graph1_opts": waste_cols,
    "graph2_fn": waste_graph2
})

# 3. Community Awareness
comm_cols = get_columns_by_prefix(df, "Community Awareness_")

def comm_graph2(dff, screen_width=None):
    if dff.empty:
        return no_data_fig()
    
    # Find sessions and communities columns
    sessions_cols = [col for col in get_columns_by_prefix(dff, "Community Awareness_") if "Sessions" in col]
    communities_cols = [col for col in get_columns_by_prefix(dff, "Community Awareness_") if "Communities" in col]
    
    if sessions_cols and communities_cols:
        # Handle NaN values by filling with 0 before sum
        vals = [dff[sessions_cols[0]].fillna(0).sum(), dff[communities_cols[0]].fillna(0).sum()]
        names = ["Sessions", "Communities"]
        
        # Check if we have any meaningful data
        if all(v <= 0 for v in vals):
            return no_data_fig("No community engagement data available")
    else:
        return no_data_fig("No community engagement data available")
        
    fig = px.pie(values=vals, names=names, hole=0.4, title="Distribution of Engagement Methods")
    fig.update_layout(height=350, margin=dict(t=60, b=40, l=40, r=20))

    # Mobile legend
    if screen_width and screen_width < 768:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=60, b=100, l=40, r=20)
        )
    return fig 
sections_config.append({
    "id": "comm",
    "title": "👥 Community Awareness",
    "kpi_cols": comm_cols[:4] if len(comm_cols) >= 4 else comm_cols,
    "graph1_defaults": [comm_cols[0], comm_cols[1]] if len(comm_cols) >= 2 else comm_cols,
    "graph1_opts": comm_cols,
    "graph2_fn": comm_graph2
})

# 4. Residential Societies
res_cols = get_columns_by_prefix(df, "Awareness in Residential Socities_")
# Add RWA participants from beach clean up if available
rwa_cols = [col for col in get_columns_by_prefix(df, "Beach Clean Up_") if "RWA" in col]
res_cols = res_cols + rwa_cols[:1] if rwa_cols else res_cols

def res_graph2(dff, screen_width=None):
    if dff.empty:
        return no_data_fig()
    
    # Get residential society columns for scatter plot
    res_available = get_columns_by_prefix(dff, "Awareness in Residential Socities_")
    
    if len(res_available) >= 3:
        x_col, y_col, size_col = res_available[0], res_available[1], res_available[2]
        
        # Create a clean dataframe with no NaN values for plotting
        plot_df = dff[[x_col, y_col, size_col]].copy()
        
        # Fill NaN values with 0 for plotting
        plot_df = plot_df.fillna(0)
        
        # Remove rows where all values are 0 (which would be invisible anyway)
        plot_df = plot_df[(plot_df[x_col] > 0) | (plot_df[y_col] > 0) | (plot_df[size_col] > 0)]
        
        if plot_df.empty:
            return no_data_fig("No valid data for residential society scatter plot")
        
        # Ensure size values are positive (scatter plot requires positive sizes)
        plot_df[size_col] = plot_df[size_col].abs()
        plot_df.loc[plot_df[size_col] == 0, size_col] = 1  # Replace 0 with 1 for minimum size
        
        fig = px.scatter(plot_df, x=x_col, y=y_col, size=size_col, 
                        title="Distribution of Societies by Engagement",
                        labels={x_col: short_label(x_col),
                               y_col: short_label(y_col),
                               size_col: short_label(size_col)})
    else:
        return no_data_fig("Insufficient residential society data available")
        
    fig.update_layout(height=350, margin=dict(t=60, b=40, l=40, r=20))

    # Mobile legend
    if screen_width and screen_width < 768:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=60, b=100, l=40, r=20)
        )
    return fig

sections_config.append({
    "id": "res",
    "title": "🏘 Awareness in Residential Societies",
    "kpi_cols": res_cols[:4] if len(res_cols) >= 4 else res_cols,
    "graph1_defaults": [res_cols[0], res_cols[1]] if len(res_cols) >= 2 else res_cols,
    "graph1_opts": res_cols,
    "graph2_fn": res_graph2
})

# 5. Educational Institutions
def edu_graph2(dff, screen_width=None):
    if dff.empty:
        return no_data_fig()

    # Get all columns with the prefix
    edu_cols = get_columns_by_prefix(dff, "Awareness in Educational Institutions_")

    if not edu_cols:
        return no_data_fig("No educational institution data available")

    # Aggregate values
    vals = dff[edu_cols].fillna(0).sum().values
    names = [col.replace("Awareness in Educational Institutions_", "") for col in edu_cols]

    if all(v <= 0 for v in vals):
        return no_data_fig("No educational institution data available")

    # Check screen size
    if screen_width and screen_width < 768:
        # Mobile → vertical bar chart
        fig = px.bar(
            x=names,
            y=vals,
            text=vals,
            title="Awareness in Educational Institutions",
            labels={"x": "Category", "y": "Count"}
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=500,
            margin=dict(t=60, b=120, l=40, r=40),  # space for rotated labels
            xaxis_tickangle=-45
        )
    else:
        # Desktop → horizontal bar chart
        fig = px.bar(
            x=vals,
            y=names,
            orientation="h",
            text=vals,
            title="Awareness in Educational Institutions",
            labels={"x": "Count", "y": "Category"}
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            height=500,
            margin=dict(t=60, b=40, l=150, r=40),
            yaxis=dict(autorange="reversed")
        )

    return fig


# 6. Overall Awareness Impact
overall_cols = get_columns_by_prefix(df, "Overall Awareness Impact_")

def overall_graph2(dff, screen_width=None):
    if dff.empty:
        return no_data_fig()
    
    # Get fresh overall columns from current dataframe
    overall_cols_available = get_columns_by_prefix(dff, "Overall Awareness Impact_")
    
    if overall_cols_available:
        # Create a clean dataframe for sunburst
        plot_df = dff[["Year Period", overall_cols_available[0]]].copy()
        plot_df = plot_df.fillna(0)
        
        # Remove rows with zero or negative values
        plot_df = plot_df[plot_df[overall_cols_available[0]] > 0]
        
        if plot_df.empty:
            return no_data_fig("No positive values for overall impact visualization")
        
        fig = px.sunburst(plot_df, path=["Year Period"], values=overall_cols_available[0], 
                         title="Impact Growth Over Time")
    else:
        return no_data_fig("No overall impact data available")
        
    fig.update_layout(height=350, margin=dict(t=60, b=40, l=40, r=20))

    # Mobile legend
    if screen_width and screen_width < 768:
        fig.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
            margin=dict(t=60, b=100, l=40, r=20)
        )
    return fig

sections_config.append({ 
    "id": "overall",
    "title": "📊 Overall Awareness Impact",
    "kpi_cols": overall_cols[:4] if len(overall_cols) >= 4 else overall_cols,
    "graph1_defaults": [overall_cols[0], overall_cols[1]] if len(overall_cols) >= 2 else overall_cols,
    "graph1_opts": overall_cols,
    "graph2_fn": overall_graph2
})

# def layout():
#     if not current_user.is_authenticated:
#         return dcc.Location(pathname="/", id="redirect-login")

#     return html.Div([

#         # ================= HEADER (Yellow Band) =================
#         html.Div([
#             html.Div([
#                 # Logo positioned at the left
#                 html.Img(
#                     src="/assets/Khushiyaan Logo.jpg",
#                     className="login-logo",
#                     style={
#                         "height": "50px",
#                         "marginRight": "20px",
#                         "position": "absolute",
#                         "left": "20px",
#                         "top": "50%",
#                         "transform": "translateY(-50%)"
#                     }
#                 ),

#                 # Welcome text (centered)
#                 html.H4(
#                     f"👋 Hello {current_user.id}! Welcome to the Khushiyaan Foundation Dashboard",
#                     className="header-title",
#                     style={
#                         "margin": "0",
#                         "fontWeight": "bold",
#                         "fontSize": "22px",
#                         "color": "#003366",
#                         "flex": "1",
#                         "textAlign": "center",
#                         "paddingLeft": "80px"
#                     }
#                 ),

#                 # Logout button (right side)
#                 dbc.Button(
#                     "Logout",
#                     id="logout-button",
#                     color="danger",
#                     size="sm",
#                     className="logout-button",
#                     style={
#                         "backgroundColor": "#dc3545",
#                         "borderColor": "#dc3545",
#                         "color": "white",
#                         "fontWeight": "bold",
#                         "padding": "8px 16px",
#                         "borderRadius": "6px",
#                         "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
#                         "fontSize": "14px",
#                         "position": "absolute",
#                         "right": "20px"
#                     }
#                 )
#             ], className="header-top", style={
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center",
#                 "position": "relative",
#                 "width": "100%",
#                 "padding": "0 20px"
#             })
#         ], className="header-wrapper", style={
#             "backgroundColor": "#FFCC00",  # Yellow band
#             "padding": "15px 0",
#             "marginTop": "0px",
#             "margin": "0",
#             "width": "100vw",
#             "position": "relative",
#             "left": "50%",
#             "transform": "translateX(-50%)",
#             "boxShadow": "0px 2px 5px rgba(0,0,0,0.1)"
#         }),

def layout():
    if not current_user.is_authenticated:
        return dcc.Location(pathname="/", id="redirect-login")

    client = session.get("client")  # Get user role from session
    ADMIN_CLIENT = os.getenv("ADMIN_CLIENT")

    return html.Div([

        # ================= HEADER (Yellow Band) =================
        html.Div([
            html.Div([
                # Logo (Left)
                html.Img(
                    src="/assets/Khushiyaan Logo.jpg",
                    style={
                        "height": "50px",
                        "position": "absolute",
                        "left": "20px",
                        "top": "50%",
                        "transform": "translateY(-50%)"
                    }
                ),

                # Welcome Text (Center)
                html.H4(
                    f"👋 Hello {current_user.id}! Welcome to the Khushiyaan Foundation Dashboard",
                    style={
                        "margin": "0",
                        "fontWeight": "bold",
                        "fontSize": "22px",
                        "color": "#003366",
                        "flex": "1",
                        "textAlign": "center",
                        "paddingLeft": "80px"
                    }
                ),

                # Action Buttons (Right)
                html.Div([
                    # 📨 Show Send Certificates only for Admin
                    (
                        dbc.Button(
                            "Send Certificates",
                            id="send-certificates",
                            color="primary",
                            size="sm",
                            style={
                                "backgroundColor": "#001F54",
                                "border": "none",
                                "color": "white",
                                "fontWeight": "bold",
                                "padding": "8px 16px",
                                "borderRadius": "6px",
                                "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                                "fontSize": "14px",
                                "marginRight": "10px",
                                "transition" : "0.3s ease-in-out"
                            }
                        )
                        if client == ADMIN_CLIENT else None
                    ),

                    # 🔴 Logout Button (Always Visible)
                    dbc.Button(
                        "Logout",
                        id="logout-button",
                        color="danger",
                        size="sm",
                        style={
                            "backgroundColor": "#dc3545",
                            "borderColor": "#dc3545",
                            "color": "white",
                            "fontWeight": "bold",
                            "padding": "8px 16px",
                            "borderRadius": "6px",
                            "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                            "fontSize": "14px"
                        }
                    )
                ], style={
                    "position": "absolute",
                    "right": "20px",
                    "display": "flex",
                    "alignItems": "center"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "position": "relative",
                "width": "100%",
                "padding": "0 20px"
            })
        ], style={
            "backgroundColor": "#FFCC00",
            "padding": "15px 0",
            "width": "100vw",
            "boxShadow": "0px 2px 5px rgba(0,0,0,0.1)"
        }),

        # ================= Redirect Location =================
        dcc.Location(id="logout-redirect", refresh=True),

        # ================= ORIGINAL TITLE =================
        html.H2(
            "Impact Metrics",
            style={
                "textAlign": "center",
                "marginTop": "10px",
                "fontWeight": "700",
                "color": "#003366"
            }
        ),
        dcc.Location(id="url"),

        # ================= FILTERS =================
        html.Div([
            # Location Filter Row
            dbc.Row([
                dbc.Col(
                    html.Div(
                        "Select Location:",
                        style={"fontWeight": "600", "paddingTop": "8px", "color": "#003366"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="global-location-dropdown",
                        options=[{"label": "All Locations", "value": "All"}] +
                                [{"label": location, "value": location} for location in available_locations],
                        value="All",
                        clearable=False,
                        style={
                            "border": "2px solid #003366",
                            "borderRadius": "8px",
                            "backgroundColor": "#FFF8E1",
                            "minWidth": "250px"
                        }
                    ),
                    width="auto"
                )
            ], justify="center", align="center", style={"marginBottom": "15px"}),

            # Year Period Filter Row
            dbc.Row([
                dbc.Col(
                    html.Div(
                        "Select Year Period:",
                        style={"fontWeight": "600", "paddingTop": "8px", "color": "#003366"}
                    ),
                    width="auto"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="global-year-period-dropdown",
                        options=[{"label": "All Year Periods", "value": "All"}] +
                                [{"label": year_period, "value": year_period} for year_period in available_year_periods],
                        value="All",
                        clearable=False,
                        style={
                            "border": "2px solid #003366",
                            "borderRadius": "8px",
                            "backgroundColor": "#FFF8E1",
                            "minWidth": "200px"
                        }
                    ),
                    width="auto"
                )
            ], justify="center", align="center")
        ], style={"textAlign": "center", "marginTop": "20px", "marginBottom": "20px"}),

        # ================= SECTIONS CONTAINER =================
        html.Div(
            id="sections-container",
            children=[],
            style={
                "padding": "20px",
                "backgroundColor": "#F5F5F5",
                "borderRadius": "12px",
                "boxShadow": "0px 3px 8px rgba(0,0,0,0.05)",
                "marginBottom": "0px"
            }
        )
    ], style={
        "fontFamily": "Arial, sans-serif",
        "marginBottom": "0px",
        "paddingBottom": "0px"
    })
 
# ---------------- Callbacks ----------------
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import dash
from dash.dependencies import Input, Output

@dash.callback(
    Output("send-certificates", "children"),
    Input("send-certificates", "n_clicks"),
    prevent_initial_call=True
)
def send_all_certificates(n_clicks):
    if n_clicks <= 0:
        return "Send Certificates"

    try:
        start_total = time.perf_counter()

        df = fetch_form_responses("Khushiyan Foundation (Responses)")
        total = df.shape[0]

        print(f"🔵 Starting parallel processing for {total} certificates…")

        # store successfully processed row numbers for batch updating
        rows_to_update = []
        
        # -------- FUNCTION FOR EACH USER --------
        def process_user(row,smtp_client):
            try:
                user_start = time.perf_counter()

                name = row["Name"]
                email = row["Email"]
                event = row["Event"]
                date_str = row["Date"]
                location = row["Location"]
                sponsor = row["Sponsor"]
                photo_path = row["Upload the image of the event"]

                date = format_pretty_date(date_str)
                cert_path = f"certificates/{name}_certificate.pdf"

                # -------- Certificate generation --------
                t1 = time.perf_counter()
                generate_certificate(
                    name=name,
                    event_name=event,
                    location=location,
                    date=date,
                    sponsor=sponsor,
                    template_path="assets/Legrand template.pdf",
                    output_path=cert_path,
                    photo_path=photo_path
                )
                t2 = time.perf_counter()

                # -------- Email sending --------
                send_certificate_mail(
                    smtp_client,
                    receiver_email=email,
                    subject=f"Khushiyaan Foundation - {event} Certificate",
                    body=f"Hello {name},\n\nThank you for participating in the {event} Drive on {date}!\nPlease find your certificate attached.\n\nWarm regards,\nKhushiyaan Foundation",
                    attachments=[cert_path]
                )
                t3 = time.perf_counter()

                total_time = time.perf_counter() - user_start

                print(
                    f"🟢 {name} processed | PDF: {t2 - t1:.2f}s | Email: {t3 - t2:.2f}s | Total: {total_time:.2f}s"
                )

                return row["sheet_row"]  # send sheet row back

            except Exception as e:
                print(f"❌ Error for {row['Name']}: {e}")
                return None

        # -------- PARALLEL EXECUTION --------
        max_workers = 1  # adjust based on CPU / Gmail limits

        # Create one SMTP client per worker
        smtp_clients = [create_smtp_client() for _ in range(max_workers)]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            
            futures = {}
            client_index = 0  # round-robin pointer

            for _, row in df.iterrows():
                
                # pick one SMTP client for this job
                smtp_client = smtp_clients[client_index]
                client_index = (client_index + 1) % max_workers
                
                # submit the job with the client
                future = executor.submit(process_user, row, smtp_client)
                futures[future] = row

            # collect results
            for future in as_completed(futures):
                result = future.result()
                if result:
                    rows_to_update.append(result)
        # close all smtp clients at end
        for client in smtp_clients:
            try:
                client.quit()
            except:
                pass
        print("Reached here")
        update_sheet("Khushiyan Foundation (Responses)",rows_to_update)
        # -------- DONE --------
        end_total = time.perf_counter()
        print(f"\n🎉 ALL DONE in {end_total - start_total:.2f}s")

        return "All Sent!"

    except Exception as e:
        print("Error:", e)
        return str(e)

@dash.callback(
    Output("sections-container", "children"),
    Input("global-location-dropdown", "value"),
    Input("global-year-period-dropdown", "value"),
    State("screen-width", "data"),
)
def update_sections(selected_location, selected_year_period, screen_width_store):
    dff=get_filtered_df()
    
    print("screen_width_store:", screen_width_store) # Debugging line to check screen width
    print(f"Selected location: {selected_location}") # Debug selected location
    print(f"Selected year period: {selected_year_period}") # Debug selected year period
    
    if selected_year_period is None or selected_location is None:
        return dbc.Alert("⚠ Please select valid filters.", color="danger")

    screen_width = screen_width_store or 1200  # default 1200 if None

    if selected_location != 'All':
        dff = dff[dff.location == selected_location]
    
    # Remove location column and clean data
    if "location" in dff.columns:
        df_clean = dff.drop(columns=["location"], axis=1)
    else:
        df_clean = dff.copy()
        
    # Replace "" with NaN
    df_clean = df_clean.replace("", np.nan)
    
    # Convert all but Year Period column to float
    for col in df_clean.columns:
        if col != "Year Period":
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    
    # Group and sum by Year Period
    if "Year Period" in df_clean.columns:
        summary = df_clean.groupby("Year Period", dropna=True).sum(numeric_only=True).reset_index()
    else:
        summary = df_clean.copy()
    
    # Now apply year period filtering on the summary data
    if selected_year_period != "All":
        summary = summary[summary["Year Period"] == selected_year_period] if "Year Period" in summary.columns else summary.copy()
    
    # Use summary as our working dataset
    dff = summary
    
    print(f"Filtered data shape: {dff.shape}")  # Debug filtered data
    children = []
    
    # Recreate sections_config dynamically to ensure fresh column discovery
    dynamic_sections_config = []

    # Build sections configuration dynamically
    # 1. Beach Clean Up
    beach_cols_dynamic = get_columns_by_prefix(df, "Beach Clean Up_")
    beach_waste_cols = [col for col in get_columns_by_prefix(df, "Waste Management_") 
                       if "Debris" in col or "Total Waste" in col]
    beach_cols_dynamic = beach_cols_dynamic + beach_waste_cols[:1] if beach_waste_cols else beach_cols_dynamic
    
    if beach_cols_dynamic:
        dynamic_sections_config.append({
            "id": "beach",
            "title": "🏖 Beach Clean Up",
            "kpi_cols": beach_cols_dynamic[:4],
            "graph1_defaults": beach_cols_dynamic[:2] if len(beach_cols_dynamic) >= 2 else beach_cols_dynamic,
            "graph1_opts": beach_cols_dynamic,
            "graph2_fn": beach_graph2
        })
    
    # 2. Waste Management
    waste_cols_dynamic = get_columns_by_prefix(df, "Waste Management_")
    if waste_cols_dynamic:
        dynamic_sections_config.append({
            "id": "waste",
            "title": "♻ Waste Management",
            "kpi_cols": waste_cols_dynamic[:4],
            "graph1_defaults": waste_cols_dynamic[:2] if len(waste_cols_dynamic) >= 2 else waste_cols_dynamic,
            "graph1_opts": waste_cols_dynamic,
            "graph2_fn": waste_graph2
        })
    
    # 3. Community Awareness
    comm_cols_dynamic = get_columns_by_prefix(df, "Community Awareness_")
    if comm_cols_dynamic:
        dynamic_sections_config.append({
            "id": "comm",
            "title": "👥 Community Awareness",
            "kpi_cols": comm_cols_dynamic[:4],
            "graph1_defaults": comm_cols_dynamic[:2] if len(comm_cols_dynamic) >= 2 else comm_cols_dynamic,
            "graph1_opts": comm_cols_dynamic,
            "graph2_fn": comm_graph2
        })
    
    # 4. Residential Societies
    res_cols_dynamic = get_columns_by_prefix(df, "Awareness in Residential Socities_")
    rwa_cols = [col for col in get_columns_by_prefix(df, "Beach Clean Up_") if "RWA" in col]
    res_cols_dynamic = res_cols_dynamic + rwa_cols[:1] if rwa_cols else res_cols_dynamic
    if res_cols_dynamic:
        dynamic_sections_config.append({
            "id": "res",
            "title": "🏘 Awareness in Residential Societies",
            "kpi_cols": res_cols_dynamic[:4],
            "graph1_defaults": res_cols_dynamic[:2] if len(res_cols_dynamic) >= 2 else res_cols_dynamic,
            "graph1_opts": res_cols_dynamic,
            "graph2_fn": res_graph2
        })
    
    # 5. Educational Institutions
    edu_cols_dynamic = get_columns_by_prefix(df, "Awareness in Educational Institutions_")
    if edu_cols_dynamic:
        dynamic_sections_config.append({
            "id": "edu",
            "title": "🎓 Awareness in Educational Institutions",
            "kpi_cols": edu_cols_dynamic[:4],
            "graph1_defaults": edu_cols_dynamic[:2] if len(edu_cols_dynamic) >= 2 else edu_cols_dynamic,
            "graph1_opts": edu_cols_dynamic,
            "graph2_fn": edu_graph2
        })
    
    # 6. Overall Awareness Impact
    overall_cols_dynamic = get_columns_by_prefix(df, "Overall Awareness Impact_")
    if overall_cols_dynamic:
        dynamic_sections_config.append({
            "id": "overall",
            "title": "📊 Overall Awareness Impact",
            "kpi_cols": overall_cols_dynamic[:4],
            "graph1_defaults": overall_cols_dynamic[:2] if len(overall_cols_dynamic) >= 2 else overall_cols_dynamic,
            "graph1_opts": overall_cols_dynamic,
            "graph2_fn": overall_graph2
        })
    
    print(f"Dynamic sections created: {len(dynamic_sections_config)}")  # Debug sections
    
    for sec in dynamic_sections_config:
        # KPIs
        kpi_cards = []
        for i, col in enumerate(sec["kpi_cols"]):
            val = float(dff[col].sum()) if (not dff.empty and col in dff.columns) else 0.0
            title = short_label(col)
            kpi_cards.append(kpi_card(title, val, gradients[i % len(gradients)]))

        # Graph components
        graph1_comp = dual_axis_component(sec["id"], sec["graph1_defaults"][0], sec["graph1_defaults"][1],
                                         sec["graph1_opts"])
        graph2_fig = sec["graph2_fn"](dff, screen_width)

        section_div = html.Div([
            html.H3(sec["title"], style={"marginTop": "36px", "marginBottom": "12px", "fontWeight": "bold"}),
            dbc.Row([dbc.Col(card, xs=6, md=3) for card in kpi_cards], className="g-3", style={"marginBottom": "18px"}),
        dbc.Row([

    # Left chart (dual-axis)
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                graph1_comp
            ]),
            style={"height": "100%"}
        ),
        xs=12, md=6, style={"marginBottom": "15px"}
    ),

    # Right chart (graph2)
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=graph2_fig,
                    style={"height": "350px", "width": "100%"},
                    className="graph-figure",
                    config={"responsive": True}
                )
            ]),
            style={"height": "100%", "overflow":"hidden"}
        ),
        xs=12, md=6, style={"marginBottom": "15px"}
    )
])
 ])
        children.append(section_div)

    full_table = html.Div([
        html.H4("📊 Full Dataset", style={"marginTop": "40px", "fontWeight": "bold","fontFamily":"Arial, sans-serif","color":"#0c1b36"}),
        dash_table.DataTable(
            id="full-dataset-table",
            columns=[{"name": i, "id": i} for i in dff.columns],
            data=dff.to_dict("records"),
            page_size=10,  # show 10 rows per page
            style_table={
            "overflowX": "auto",
            "maxHeight": "500px",
            "overflowY": "auto",
            "width": "100%",
            "border": "1px solid #ddd",
            "borderRadius": "8px",
            "padding": "10px",
            "backgroundColor": "#f9f9f9"
        },

            style_header={
            "backgroundColor": "#B0B0B0",
            "color": "000000",
            "fontWeight": "bold",
            "textAlign": "center",
            "fontSize": "14px",
            "fontFamily": "Arial, sans-serif",
        },

            style_cell={
            "textAlign": "left",
            "padding": "10px",
            "whiteSpace": "normal",
            "fontFamily": "Arial, sans-serif",
            "fontSize": "13px",
            "color": "#333"
        },

            style_data_conditional=[
           {
            "if": {"row_index": "odd"},
            "backgroundColor": "#f2f2f2"
           },
           {
             "if": {"state": "active"},  # row being clicked
             "backgroundColor": "#ffe0b2",
             "border": "1px solid #ff7f50"
           },
           {
             "if": {"state": "selected"},  # selected row
             "backgroundColor": "#FFD700",
             "color": "#000",
             "fontWeight": "bold"
           }
       ],

            style_as_list_view=True,
            fill_width=True
        ),
        dbc.Button("Download Full Dataset", id="download-btn", className="mt-4",
        style={"backgroundColor":"#008080","borderColor":"#008080","color":"#ffffff","fontWeight":"bold","padding":"10px 20px","fontSize":"16px","marginBottom":"30px"}),
        dcc.Download(id="download-dataframe-csv")
    ])
    children.append(full_table)
   
             # Footer container mirroring banner structure
    footer = html.Div(
    [
        html.Div(
            [
                # Left Section - Khushiyaan Foundation Info + Social
                html.Div(
                    children=[
                        html.A(
                            "Khushiyaan Foundation",
                            href="https://khushiyaanfoundation.org",
                            target="_blank",
                            style={
                                "fontWeight": "bold",
                                "color": "#ffffff",
                                "textDecoration": "none",
                            },
                        ),
                        html.Br(),
                        html.Span(
                            "📍 603, Sakura Enclave, Opp Gav Hindu Hotel, "
                            "Anand Nagar GB Road, Thane, Mumbai 400615",
                            style={"fontSize": "13px", "color": "#d1d1d1"},
                        ),
                        html.Br(),
                        html.Span(
                            "📞 +91 7979818248 | ✉️ info@khushiyaanfoundation.org",
                            style={"fontSize": "13px", "color": "#d1d1d1"},
                        ),
                        html.Br(),
                        # Social Media Icons Row
                        html.Div(
                            children=[
                                html.A(
                                    html.I(className="fab fa-facebook fa-lg"),
                                    href="https://www.facebook.com/khushiyaanorg?mibextid=ZbWKwL",
                                    target="_blank",
                                    style={
                                        "margin": "0 8px",
                                        # "color": "#3b5998",
                                        "backgroundColor": "#FFD700",  # yellow circle
                                        "color": "#ffffff",            # white icon
                                        "borderRadius": "50%",
                                        "padding": "10px",
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "36px",
                                        "height": "36px",
                                        "textAlign": "center",                                                       
                                    },
                                ),
                                html.A(
                                    html.I(className="fab fa-twitter fa-lg"),
                                    href="https://x.com/Khushiyaan_Org?t=hXiEg9mKiLw5q5SuON92UA&s=08",
                                    target="_blank",
                                    style={
                                        "margin": "0 8px",
                                        # "color": "#1DA1F2",
                                        "backgroundColor": "#FFD700",  # yellow circle
                                        "color": "#ffffff",            # white icon
                                        "borderRadius": "50%",
                                        "padding": "10px",
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "36px",
                                        "height": "36px",
                                        "textAlign": "center",
                                    },
                                ),
                                html.A(
                                    html.I(className="fab fa-instagram fa-lg"),
                                    href="https://www.instagram.com/khushiyaanorg?igshid=NTc4MTIwNjQ2YQ%3D%3D",
                                    target="_blank",
                                    style={
                                        "margin": "0 8px",
                                        # "color": "#E4405F",
                                        "backgroundColor": "#FFD700",  # yellow circle
                                        "color": "#ffffff",            # white icon
                                        "borderRadius": "50%",
                                        "padding": "10px",
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "36px",
                                        "height": "36px",
                                        "textAlign": "center",
                                    },
                                ),
                                html.A(
                                    html.I(className="fab fa-linkedin in"),
                                    href="https://www.linkedin.com/company/khushiyaan-foundation/posts/?feedView=all",
                                    target="_blank",
                                    style={
                                        "margin": "0 8px",
                                        # "color": "#3b5998",
                                        "backgroundColor": "#FFD700",  # yellow circle
                                        "color": "#ffffff",            # white icon
                                        "borderRadius": "50%",
                                        "padding": "10px",
                                        "display": "inline-flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "width": "36px",
                                        "height": "36px",
                                        "textAlign": "center",                                                       
                                    },
                                ),
                            ],
                            style={"marginTop": "10px"},
                        ),
                    ]
                ),

                # Right Section - Developer Info
                html.Div(
                    children=[
                        html.Span(
                            "Developed by ",
                            style={"fontSize": "14px", "color": "#ffffff"},
                        ),
                        html.A(
                            "Clint",
                            href="https://www.linkedin.com/company/climate-and-technology-solutions/",
                            target="_blank",
                            style={
                                "fontWeight": "bold",
                                "color": "#FFD700",  # Golden highlight
                                "textDecoration": "none",
                            },
                        ),
                    ],
                    style={"fontSize": "14px", "color": "#ffffff"},
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "flexWrap": "wrap",
                "width": "100%",
                "padding": "0 20px",
            },
        )
    ],
    style={
        "backgroundColor": "#0c1b36",
        "padding": "15px 0",
        "margin": "0",
        "width": "100vw",
        "position": "relative",
        "left": "50%",
        "transform": "translateX(-50%)",
        "borderTop": "1px solid #222",
        "color": "#ffffff",
        "marginTop": "40px",
    },
    )

    children.append(footer)   

    return children


@dash.callback(
    Output({"type": "dual-axis-graph", "section": MATCH}, "figure"),
    Input({"type": "y1", "section": MATCH}, "value"),
    Input({"type": "y2", "section": MATCH}, "value"),
    Input("global-location-dropdown", "value"),
    Input("global-year-period-dropdown", "value"),
    State("screen-width", "data"),
)
def update_dual_axis_graph(y1_col, y2_col, selected_location, selected_year_period, screen_width):
    dff=get_filtered_df()
    if screen_width is None:
        screen_width = 1200

    if selected_location != 'All':
        dff = dff[dff.location == selected_location]
    
    # Remove location column and clean data
    if "location" in dff.columns:
        df_clean = dff.drop(columns=["location"], axis=1)
    else:
        df_clean = dff.copy()
        
    # Replace "" with NaN
    df_clean = df_clean.replace("", np.nan)
    
    # Convert all but Year Period column to float
    for col in df_clean.columns:
        if col != "Year Period":
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    
    # Group and sum by Year Period
    if "Year Period" in df_clean.columns:
        summary = df_clean.groupby("Year Period", dropna=True).sum(numeric_only=True).reset_index()
    else:
        summary = df_clean.copy()
    
    # Now apply year period filtering on the summary data
    if selected_year_period != "All":
        summary = summary[summary["Year Period"] == selected_year_period] if "Year Period" in summary.columns else summary.copy()
    
    # Use summary as our working dataset
    dff = summary
    fig = go.Figure()

    # Both as lines
    if y1_col in dff.columns:
        fig.add_trace(go.Scatter(x=dff["Year Period"], y=dff[y1_col], name=short_label(y1_col),
                                 line=dict(color=Y1_COLOR, width=3)))
    if y2_col in dff.columns:
        fig.add_trace(go.Scatter(x=dff["Year Period"], y=dff[y2_col], name=short_label(y2_col),
                                 line=dict(color=Y2_COLOR, width=3), yaxis="y2"))

    # Desktop: legend at right; Mobile: legend above plot
        
    if screen_width and screen_width < 768:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=130, b=60, l=40, r=40)  # Increased top margin for space between title and legend
        )
    else:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=90, b=60, l=40, r=40),  
            height=450  
        )

    fig.update_layout(
        title="Impact Metrics",
        title_x=0.5,
        title_y=0.95, 
        xaxis=dict(title="Year Period", tickangle=-45),
        yaxis=dict(title=short_label(y1_col)),
        yaxis2=dict(title=short_label(y2_col), overlaying="y", side="right"),
        height=350,
        autosize=True
    )

    return fig
    
@dash.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_full_dataset(n_clicks):
    if n_clicks is None:
        return dash.no_update
    
    try:
        # Filter the data to remove any NaN or problematic values
        df_clean = df.copy()
        df_clean = df_clean.fillna('')  # Replace NaN with empty strings
        
        return dcc.send_data_frame(
            df_clean.to_csv, 
            "Khushiyaan_Foundation_Programme_Impact.csv", 
            index=False
        )
    except Exception as e:
        print(f"Download error: {e}")
        return dash.no_update

# Logout callback
@dash.callback(
    Output("logout-redirect", "pathname"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        logout_user()  # Log out the current user
        return "/"  # Redirect to login page
    return dash.no_update    


