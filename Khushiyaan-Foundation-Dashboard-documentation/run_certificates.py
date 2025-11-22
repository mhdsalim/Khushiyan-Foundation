from utils.send_all_certificates_logic import send_all_cert_logic

if __name__ == "__main__":
    print("\n⏰ Running scheduled certificate processing job…")
    send_all_cert_logic()
    print("✅ Job completed!\n")
