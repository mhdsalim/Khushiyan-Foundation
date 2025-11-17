import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_certificate_mail(receiver_email, subject, body, attachments=None):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender_email or not password:
        raise ValueError("❌ Missing EMAIL_USER or EMAIL_PASS in .env file")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach files if any
    if attachments:
        for file in attachments:
            with open(file, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file)

                if file.endswith(".pdf"):
                    msg.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="pdf",
                        filename=file_name
                    )
                elif file.endswith((".png", ".jpg", ".jpeg")):
                    msg.add_attachment(
                        file_data,
                        maintype="image",
                        subtype=file.split(".")[-1],
                        filename=file_name
                    )
                else:
                    msg.add_attachment(
                        file_data,
                        maintype="application",
                        subtype="octet-stream",
                        filename=file_name
                    )  # fallback for other files

    # Send email securely
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.send_message(msg)

    print(f"✅ Mail sent to {receiver_email}")