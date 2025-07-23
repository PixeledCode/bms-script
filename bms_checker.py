from playwright.sync_api import sync_playwright
import smtplib, ssl
from email.message import EmailMessage
import os

MOVIE_NAME = "Jurassic World: Rebirth"
BOOKMYSHOW_URL = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=english"

GMAIL_USER = os.environ['GMAIL_USER']
GMAIL_PASS = os.environ['GMAIL_PASS']
TO_EMAIL = os.environ['TO_EMAIL']

def check_movie_available():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(BOOKMYSHOW_URL, timeout=60000)
            content = page.content()
            browser.close()
            return MOVIE_NAME.lower() in content.lower()
    except Exception as e:
        print(f"Playwright error: {e}")
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
