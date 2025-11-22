from utils.google_sheet import fetch_form_responses,format_pretty_date,update_sheet
from utils.certificate_generator import generate_certificate
from utils.mailer import send_certificate_mail
import asyncio
import time
def send_all_cert_logic():
    try:
            start_total = time.perf_counter()
            
            df = fetch_form_responses("Khushiyan Foundation (Responses)")
            total = df.shape[0]
            semaphore = asyncio.Semaphore(2)
            print(f"🔵 Starting parallel processing for {total} certificates…")

            # store successfully processed row numbers for batch updating
            rows_to_update = []
            
            # -------- FUNCTION FOR EACH USER --------
            async def process_user(row): 
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

                    # -------- PDF GENERATION --------
                    t1 = time.perf_counter()
                    generate_certificate(
                        name=name,
                        event_name=event,
                        location=location,
                        date=date,
                        sponsor=sponsor,
                        template_path="assets/base_template.pdf",
                        output_path=cert_path,
                        photo_path=photo_path
                    )
                    t2 = time.perf_counter()

                    # -------- EMAIL (AWAIT!) --------
                    await send_certificate_mail(
                        receiver_email=email,
                        subject=f"Khushiyaan Foundation - {event} Certificate",
                        body=f"Hello {name},\n\nThank you for participating in the {event} Drive on {date}!\nPlease find your certificate attached.\n\nWarm regards,\nKhushiyaan Foundation",
                        attachments=[cert_path]
                    )
                    t3 = time.perf_counter()

                    total_time = time.perf_counter() - user_start

                    print(f"🟢 {name} processed | PDF: {t2 - t1:.2f}s | Email: {t3 - t2:.2f}s | Total: {total_time:.2f}s")

                    return row["sheet_row"]

                except Exception as e:
                    print(f"❌ Error for {row['Name']}: {e}")
                    return None
            async def process_all_async(df):
                tasks = [process_user(row) for _, row in df.iterrows()]
                results = await asyncio.gather(*tasks)
                return [r for r in results if r]
            # -------- PARALLEL EXECUTION --------
            # max_workers = 1  # adjust based on CPU / Gmail limits

            # with ThreadPoolExecutor(max_workers=max_workers) as executor:
                
            #     futures = {}
            #     for _, row in df.iterrows():      
            #         # submit the job with the client
            #         future = executor.submit(process_user, row)
            #         futures[future] = row

            #     # collect results
            #     for future in as_completed(futures):
            #         result = future.result()
            #         if result:
            #             rows_to_update.append(result)
            rows_to_update = asyncio.run(process_all_async(df))

            update_sheet("Khushiyan Foundation (Responses)",rows_to_update)
            # -------- DONE --------
            end_total = time.perf_counter()
            print(f"\n🎉 ALL DONE in {end_total - start_total:.2f}s")

            return "All Sent!"

    except Exception as e:
        print("Error:", e)
        return str(e)