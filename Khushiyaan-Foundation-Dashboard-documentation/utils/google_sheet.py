import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

# Define the scope of the application
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
def fetch_form_responses(sheet_name):
    """
    Fetch all form responses from a Google Sheet and return them as a pandas DataFrame.
    Requires:
      - credentials.json file in project root
      - The Google Sheet shared with the service account
    """
    

    # Open the sheet by name
    sheet = client.open(sheet_name).sheet1

    # Get all data
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    df["sheet_row"] = df.index + 2
    if df.empty:
        print("⚠️ Sheet is empty.")
        return df

    col_name = "Send_or_not"

    # ---- FIND PENDING ROWS ----
    pending_df = df[df[col_name].isna() | (df[col_name].astype(str).str.strip() == "")]
    print(f"📌 Pending Certificates: {len(pending_df)}")

    # No pending rows → return empty
    if pending_df.empty:
        return pending_df

    return pending_df
def update_sheet(sheet_name, rows_to_update):
    sheet = client.open(sheet_name).sheet1
    
    # Hardcode the column index for 'Send_or_not'
    col_name = "Send_or_not"
    col_index = sheet.row_values(1).index(col_name) + 1

    updates = []
    for row_num in rows_to_update:
        updates.append({
            "range": f"{gspread.utils.rowcol_to_a1(int(row_num), col_index)}",
            "values": [["Yes"]]
        })

    sheet.batch_update(updates)
    print(f"🟢 Batch updated {len(rows_to_update)} rows")
def format_pretty_date(date_str):
    """
    Converts 13/10/2025 into 13th October 2025
    """
    # Try multiple possible formats
    possible_formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]

    parsed = None
    for fmt in possible_formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            break
        except:
            continue

    if parsed is None:
        raise ValueError("Unsupported date format:", date_str)

    day = parsed.day
    month = parsed.strftime("%B")
    year = parsed.year

    # Day suffix logic
    if 10 < day % 100 < 14:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    return f"{day}{suffix} {month} {year}"

