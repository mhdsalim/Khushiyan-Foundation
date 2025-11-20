import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_smtp_client():
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    context = ssl.create_default_context()
    client = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
    client.login(sender_email, password)

    print("🔐 Logged into SMTP once.")
    return client


def send_certificate_mail(smtp_client, receiver_email, subject, body, attachments=None):
    sender_email = os.getenv("EMAIL_USER")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Add attachments
    if attachments:
        for file in attachments:
            with open(file, "rb") as f:
                file_data = f.read()

            file_name = os.path.basename(file)
            ext = file.split(".")[-1].lower()

            msg.add_attachment(
                file_data,
                maintype="application" if ext == "pdf" else "image",
                subtype=ext,
                filename=file_name
            )

    # Use the SAME smtp client for all mails
    smtp_client.send_message(msg)
    print(f"✅ Mail sent to {receiver_email}")
    return ""

    