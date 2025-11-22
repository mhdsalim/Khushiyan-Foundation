from apscheduler.schedulers.background import BackgroundScheduler
from utils.send_all_certificates_logic import send_all_cert_logic
from datetime import datetime
import atexit

def run_cert_job():
    print(f"\n⏰ Cron Triggered at {datetime.now()} …")
    send_all_cert_logic()
    print("✅ Cron job completed!\n")

def start_scheduler():
    scheduler = BackgroundScheduler()

    # Run every day at 10 AM
    scheduler.add_job(
        run_cert_job,
        trigger="cron",
        hour=13,
        minute=38,
        id="send_certificates_job",
        replace_existing=True,
    )

    scheduler.start()
    print("🔁 Internal cron scheduler started")

    # shut down cleanly on app stop
    atexit.register(lambda: scheduler.shutdown())
