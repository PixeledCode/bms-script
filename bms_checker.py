import smtplib
import ssl
from email.message import EmailMessage
import requests
import os

# Config
MOVIE_NAME = "pride and prejudice"
BOOKMYSHOW_URL = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=english"

# Email credentials from GitHub Secrets
GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_PASS = os.environ['GMAIL_PASS']
TO_EMAIL = os.environ['TO_EMAIL']

def check_movie_available():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        res = requests.get(BOOKMYSHOW_URL, headers=headers)
        res.raise_for_status()
        return MOVIE_NAME.lower() in res.text.lower()
    except Exception as e:
        print(f"Error fetching BookMyShow page: {e}")
        return False

def send_email():
    msg = EmailMessage()
    msg.set_content(
        f"🎟️ *{MOVIE_NAME.title()}* is now listed on BookMyShow Bengaluru!\n\nLink: {BOOKMYSHOW_URL}"
    )
    msg['Subject'] = f"🎬 {MOVIE_NAME.title()} is Now on BookMyShow!"
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        print("✅ Email sent!")

if __name__ == "__main__":
    if check_movie_available():
        send_email()
    else:
        print("❌ Movie not found.")
