import os
import sys
import smtplib
from email.message import EmailMessage
from playwright.sync_api import sync_playwright

MOVIE_NAME = "Prejudice"
FLAG_FILE = ".movie_found"

def send_email():
    msg = EmailMessage()
    msg.set_content(f"{MOVIE_NAME} is now showing on BookMyShow! Book here https://in.bookmyshow.com/explore/movies-bengaluru?languages=english")
    msg["Subject"] = f"{MOVIE_NAME} is now live! 🎬"
    msg["From"] = os.environ["GMAIL_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["GMAIL_USER"], os.environ["GMAIL_PASS"])
        smtp.send_message(msg)

    print("✅ Email sent!")

    # Write flag to skip future runs
    with open(FLAG_FILE, "w") as f:
        f.write("Email sent")

def check_bms():
    if os.path.exists(FLAG_FILE):
        print("✅ Movie already found. Skipping further checks.")
        sys.exit(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            print("⏳ Visiting BookMyShow...")
            page.goto("https://in.bookmyshow.com/explore/movies-bengaluru?languages=english", timeout=60000)
            page.wait_for_selector(".kgjaGy", timeout=30000)

            content = page.content()
            if MOVIE_NAME.lower() in content.lower():
                print(f"🎉 Found movie: {MOVIE_NAME}")
                send_email()
                sys.exit(0)
            else:
                print("❌ Movie not found.")
        except Exception as e:
            print("⚠️ Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    check_bms()
