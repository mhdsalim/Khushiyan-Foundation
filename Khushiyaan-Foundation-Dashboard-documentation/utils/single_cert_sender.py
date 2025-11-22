import os
from utils.google_sheet import fetch_form_responses,format_pretty_date,update_sheet
from utils.certificate_generator import generate_certificate
from utils.mailer import send_certificate_mail
import time

def send_single_certificate(name, email,event,date_str ,location, sponsor, photo_path,row):
    """
    Generate a certificate PDF and send it to a single participant using Brevo.
    """

    try:
        user_start = time.perf_counter()
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
        update_sheet("Khushiyan Foundation (Responses)",[row])
        print(f"✅ Certificate sent to {name} ({email})")
        return {"status": "success", "email": email}

    except Exception as e:
        print(f"❌ Error sending certificate to {email}: {e}")
        return {"status": "error", "email": email, "error": str(e)}
