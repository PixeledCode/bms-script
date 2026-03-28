import os
import sys
import smtplib
from email.message import EmailMessage
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

MOVIE_ID = "MV200953"
MOVIE_NAME = "Project Hail Mary"
FLAG_FILE = ".movie_found"
VENUE_URL = "https://www.district.in/movies/pvr-nexus-formerly-forum-koramangala-bengaluru-in-bengaluru-CD1022297?fromdate=2026-03-31"
BOOKING_LINK = f"https://www.district.in/movies/project-hail-mary-movie-tickets-in-bengaluru-{MOVIE_ID}?fromdate=2026-03-31"

def send_email():
    msg = EmailMessage()
    msg.set_content(f"{MOVIE_NAME} is now showing in IMAX at PVR Nexus!\n\nBook here: {BOOKING_LINK}")
    msg["Subject"] = f"🎬 {MOVIE_NAME} IMAX is live!"
    msg["From"] = os.environ["GMAIL_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["GMAIL_USER"], os.environ["GMAIL_PASS"])
        smtp.send_message(msg)

    print("✅ Email sent!")
    with open(FLAG_FILE, "w") as f:
        f.write("Email sent")

def check_imax():
    if os.path.exists(FLAG_FILE):
        print("✅ Already notified. Skipping.")
        sys.exit(0)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            print("⏳ Visiting District...")
            page.goto(VENUE_URL, timeout=60000)

            # Wait for at least one movie link to appear
            page.wait_for_selector(f'a[href*="{MOVIE_ID}"]', timeout=15000)

            soup = BeautifulSoup(page.content(), "html.parser")

            # Anchor on the permanent movie ID in the href
            movie_link = soup.find("a", href=lambda h: h and MOVIE_ID in h)

            if not movie_link:
                print(f"❌ '{MOVIE_NAME}' not showing at this venue today.")
                sys.exit(0)

            # Walk up to the enclosing <li> which contains all showtimes for this movie
            li = movie_link.find_parent("li")
            if not li:
                print("⚠️ Could not find parent container for movie.")
                sys.exit(1)

            # Search for "IMAX 2D" as plain text anywhere within that <li>
            imax_label = li.find(string=lambda t: t and "IMAX 2D" in t)

            if imax_label:
                print(f"🎉 IMAX showing found for '{MOVIE_NAME}'!")
                send_email()
            else:
                print(f"❌ '{MOVIE_NAME}' is showing but no IMAX yet (only 4DX or other formats).")

        except Exception as e:
            print("⚠️ Error:", e)
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    check_imax()