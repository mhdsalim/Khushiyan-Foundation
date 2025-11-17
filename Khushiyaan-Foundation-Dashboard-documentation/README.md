# Khushiyaan Foundation Dashboard
An **interactive multi-page dashboard** built using **Plotly Dash** and **Bootstrap** for visualizing programme impact, waste management statistics, beach cleanups, and team contributions.  

---

## 🧭 Overview

This project consolidates multiple impact programs (like Beach Cleanup and Waste Management) into a unified web-based dashboard.  
It allows admins and team members to:
- Monitor ongoing activities.
- Visualize statistics and participation.
- Manage and update campaign data in real time.

---

## ⚙️ Tech Stack

- **Frontend:** Dash, Plotly, Bootstrap, HTML/CSS
- **Backend:** Python(Flask integrated with Dash)
- **Data:** Excel/CSV processed via Pandas
- **Email Integration:** Gmail SMTP via smtplib
- **Deployment:** Render 

---

## 📂 Project Structure  
```
Khushiyaan-Foundation-Dashboard/
│
├── assets/                            # Contains all static files (CSS, JS, and images)
│   ├── animate.js                     # Handles animations and visual transitions
│   ├── background.jpg                 # Background image for desktop view
│   ├── beach_cleanup_bg.jpeg          # Background image for mobile/responsive view
│   ├── custom.css                     # Custom CSS for dashboard styling and overrides
│   ├── Khushiyaan Logo.jpg            # Organization logo (unused variant)
│   ├── Khushiyaan_Logo-removebg-preview.png  # Transparent version of Khushiyaan logo
│   ├── login.css                      # Styling for login page UI
│   ├── programme_impact.css           # Styling for Programme Impact section
│   ├── responsive.css                 # Handles responsive layouts across devices
│   ├── set_screen_width.js            # JavaScript to detect screen width for responsiveness
│   └── styles.css                     # Global styles shared across all components
│
├── Khushiyaan-Foundation-Dashboard/   # Root project directory (main app folder)
│
├── notebooks/                         # Jupyter/analysis notebooks
│
├── pages/                             # Contains all Dash/Flask-based dashboard subpages
│   ├── beach-cleanup.py               # Visualizations for Beach Cleanup program
│   ├── beach-warriors-team.py         # Displays Beach Warriors team data
│   ├── login.py                       # Login authentication and UI logic
│   ├── programme-impact.py            # Programme Impact analytics and KPIs
│   └── waste-management.py            # Waste Management metrics and charts
│
├── utils/                             # Helper modules (utility functions)
│   └── mailer.py                      # Handles automated email sending for certificates
│
├── .env                               # Environment variables (API keys, email creds, etc.)
├── .gitignore                         # Specifies files/folders to exclude from Git
├── Procfile                           # Deployment configuration (Render/Heroku setup)
├── Programme_Impact_Final.xlsx        # Dataset for programme impact visualizations
├── README.md                          # Project documentation and setup guide
├── app.py                             # Main Flask/Dash entry point for the dashboard
├── auth.py                            # Authentication and user session management
├── navbar.py                          # Navbar and routing logic shared across pages
├── requirements.txt                   # List of Python dependencies for installation
└── test_mail.py                       # Script to test email sending functionality (SMTP)
```

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Run the dashboard locally
```bash
python app.py
```
Now open: http://127.0.0.1:8050/ in your browser. 

## Important Code Components

🔹 1. get_filtered_df() in programme-impact.py

Filters the dataset based on the logged-in client.
Admins see all data; clients see only their own.
```
def get_filtered_df():
    client = session.get("client", "all")  
    
    if client.lower() == "all":   # admin sees everything
        return df.copy()
    else:                 # specific client sees only their data
        return df[df["client"].str.strip().str.lower() == client.strip().lower()].copy()
```
---

🔹 2. Dynamic Dashboard Sections

Each dashboard section (Beach Cleanup, Waste Management, etc.) is dynamically built from column prefixes.
```
def get_columns_by_prefix(df, prefix):
    return [col for col in df.columns if col.startswith(prefix)]
```
---

🔹 3. Certificate Mailer (utils/mailer.py)

Handles sending personalized certificates via email (Only testing is done of sending mail with random pdf not certificates)
```
from email.message import EmailMessage
import smtplib, ssl

def send_certificate_mail(receiver_email, subject, body, attachments=None):
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender_email or not password:
        raise ValueError("Missing EMAIL_USER or EMAIL_PASS in .env file")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)
```
---


## 🧾 Deployment on Render

1. Push all changes to GitHub.

2. Render automatically redeploys the app whenever changes are pushed to the connected branch.

---



