# bms_checker.py
import asyncio
from playwright.async_api import async_playwright
import smtplib
import os
from email.mime.text import MIMEText

MOVIE_NAME = "Jurassic World: Rebirth"
URL = "https://in.bookmyshow.com/explore/movies-bengaluru?languages=english"

async def check_movie():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        content = await page.content()
        await browser.close()
        print(content.lower())
        return MOVIE_NAME.lower() in content.lower()

def send_email():
    sender = os.getenv("GMAIL_USER")
    password = os.getenv("GMAIL_PASS")
    recipient = sender
    subject = f"{MOVIE_NAME} is now available!"
    body = f"Check the link: {URL}"

    msg = MIMEText(body)
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

if __name__ == "__main__":
    if asyncio.run(check_movie()):
        print("🎬 Movie is available!")
        send_email()
    else:
        print("❌ Movie not found.")
