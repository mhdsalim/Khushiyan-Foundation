import os
import base64
import time
import httpx
from datetime import datetime

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_SENDER_EMAIL = os.getenv("SENDER_EMAIL")
BREVO_SENDER_NAME = os.getenv("SENDER_NAME", "")

def ts():
    """Return timestamp with milliseconds."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]
DEBUG_LOG = False
def log(msg):
    if DEBUG_LOG:
        print(f"[{ts()}] {msg}")

async def send_certificate_mail(receiver_email, subject, body, attachments=None):

    print("\n======================")
    log("STARTING SEND EMAIL ASYNC")
    print("======================")

    # 1️⃣ Build Payload
    log("Building payload")
    payload = {
        "sender": {"email": BREVO_SENDER_EMAIL, "name": BREVO_SENDER_NAME},
        "to": [{"email": receiver_email}],
        "subject": subject,
        "htmlContent": body
    }

    # 2️⃣ Attachments
    if attachments:
        payload["attachment"] = []
        for file in attachments:
            log(f"Reading attachment: {file}")
            with open(file, "rb") as f:
                file_bytes = f.read()

            log(f"Encoding attachment: {file}")
            encoded = base64.b64encode(file_bytes).decode("utf-8")

            payload["attachment"].append({
                "content": encoded,
                "name": os.path.basename(file)
            })

    # 3️⃣ Send async request
    log("Sending async request → Brevo API")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=20) as client:
        await client.post(url, json=payload, headers=headers)

    log("Brevo API responded → checking status")
    #response.raise_for_status()

    log(f"MAIL SENT ✔ to {receiver_email}")
    print("======================\n")
