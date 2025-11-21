import os
import requests
import base64

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("SENDER_EMAIL")
BREVO_SENDER_NAME = os.getenv("SENDER_NAME", "")

def send_certificate_mail( receiver_email, subject, body, attachments=None):
    """
    Send email using Brevo API but keeps the same signature as the SMTP version.
    """
    html_body = body.replace("\n", "<br>")
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "sender": {"email": BREVO_SENDER_EMAIL, "name": BREVO_SENDER_NAME},
        "to": [{"email": receiver_email}],
        "subject": subject,
        "htmlContent": html_body  # Brevo uses HTML content
    }

    # Handle attachments
    if attachments:
        payload["attachment"] = []
        for file in attachments:
            with open(file, "rb") as f:
                file_data = f.read()

            encoded = base64.b64encode(file_data).decode("utf-8")
            payload["attachment"].append({
                "content": encoded,
                "name": os.path.basename(file)
            })

    resp = requests.post(url, json=payload, headers=headers)

    try:
        resp.raise_for_status()
        print(f"✅ Mail sent to {receiver_email} via Brevo")
        return ""
    except Exception as e:
        print(f"❌ Error sending email to {receiver_email}: {resp.text}")
        raise e
