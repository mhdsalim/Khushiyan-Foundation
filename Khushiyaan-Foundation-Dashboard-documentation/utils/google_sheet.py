import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime

def fetch_form_responses(sheet_name):
    """
    Fetch all form responses from a Google Sheet and return them as a pandas DataFrame.
    Requires:
      - credentials.json file in project root
      - The Google Sheet shared with the service account
    """
    # Define the scope of the application
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authorize the client
    creds = ServiceAccountCredentials.from_json_keyfile_name("/etc/secrets/credentials.json", scope)
    client = gspread.authorize(creds)

    # Open the sheet by name
    sheet = client.open(sheet_name).sheet1

    # Get all data
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

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

    # ---- UPDATE SHEET VALUES ----
    # gspread rows start from 2 (row 1 = header)
        

    print("✅ Updated pending rows to 'Yes'.")

    return pending_df
def update_sheet(sheet_name,idx):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Authorize the client
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    records = sheet.get_all_records()
    df = pd.DataFrame(records)
    col_name = "Send_or_not"
    # Open the sheet by name
    sheet = client.open(sheet_name).sheet1
    sheet.update_cell(idx + 2, df.columns.get_loc(col_name) + 1, "Yes")
    return ""
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

