import dash
from dash import html, dcc, Input, Output
from flask import session
import os
from utils.google_sheet import fetch_form_responses,format_pretty_date,update_sheet
from utils.certificate_generator import generate_certificate
from utils.mailer import send_certificate_mail
import sys
# Register page in Dash multi-page system
dash.register_page(__name__, path="/admin-certificates", title="Send Certificates")

# Load admin role name from environment
ADMIN_CLIENT = os.getenv("ADMIN_CLIENT")

layout = html.Div(id="admin-cert-page")

# Render layout dynamically based on login role
@dash.callback(
    Output("admin-cert-page", "children"),
    Input("url", "pathname"),
    prevent_initial_call=True
)
def render_admin_page(_):
    client = session.get("client")
    print("Logged-in client:", client)

    if client == ADMIN_CLIENT:
        return html.Div([
            html.H3("📜 Certificate Automation Panel", style={"textAlign": "center", "marginBottom": "20px"}),

            html.Button(
                "Send Certificates",
                id="send-btn",
                n_clicks=0,
                style={
                    "padding": "10px 25px",
                    "fontSize": "16px",
                    "backgroundColor": "#007BFF",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "8px",
                    "cursor": "pointer"
                }
            ),
            html.Div(id="status", style={"marginTop": "30px", "textAlign": "center", "fontWeight": "bold"})
        ])

    return html.Div([
        html.H3("🚫 Access Denied", style={"textAlign": "center", "color": "red"}),
        html.P("You do not have permission to access this page.", style={"textAlign": "center"})
    ])


# Button callback – triggers the automation
@dash.callback(
    Output("status", "children"),
    Input("send-btn", "n_clicks"),
    prevent_initial_call=True
)
def send_certificates(n_clicks):
    if n_clicks > 0:
        try:
            df = fetch_form_responses("Khushiyan Foundation (Responses)")
            total = df.shape[0]

            for i, row in df.iterrows():
                print("Entered Loop")
                name = row["Name"]
                email = row["Email"]
                event = row["Event"]
                date_str  = row["Date"]
                location = row["Location"]
                sponsor = row["Sponsor"]
                photo_path = row["Upload the image of the event"]
                date = format_pretty_date(date_str)
                cert_path = f"certificates/{name}_certificate.pdf"
                print("Name:",name)
                generate_certificate(
                    name=name,
                    event_name=event,
                    location=location,
                    date=date,
                    sponsor=sponsor, 
                    template_path="assets/Legrand template.pdf",
                    output_path=cert_path,
                    photo_path = photo_path
                )
                send_certificate_mail(
                    receiver_email=email,
                    subject=f"Khushiyaan Foundation - {event} Certificate",
                    body=f"Hello {name},\n\nThank you for participating in the {event} Drive on {date}!\nPlease find your certificate attached.\n\nWarm regards,\nKhushiyaan Foundation",
                    attachments=[cert_path]
                )
                update_sheet("Khushiyan Foundation (Responses)",row.index)
                print("Updated Sheet00000")
                print(f"✅ Sent to {name} ({email}) [{i+1}/{total}]")

            return f"🎉 All {total} certificates sent successfully!"
        except Exception as e:
            return f"❌ Error occurred: {str(e)}"
    return ""