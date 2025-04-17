import requests
import smtplib
import os
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Read secrets from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
import requests
from bs4 import BeautifulSoup

def get_coursera_plus_annual_price():
    url = "https://www.coursera.org/courseraplus"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/119.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Try to locate the annual price text
        price_element = soup.find(string=lambda text: text and "Coursera Plus Annual" in text)
        if price_element:
            parent = price_element.find_parent()
            if parent:
                price_text = parent.get_text(strip=True)
                return f"Coursera Plus Annual: {price_text}"
        
        # Fallback: find a price that looks like $399/year
        price_candidates = soup.find_all(string=lambda text: text and "$" in text and "year" in text.lower())
        for candidate in price_candidates:
            if "coursera plus" in candidate.lower() or "/year" in candidate.lower():
                return f"Coursera Plus Annual: {candidate.strip()}"
        
        return "Coursera Plus Annual price not found."
    else:
        return f"Failed to fetch Coursera Plus page. Status code: {response.status_code}"


def get_frontendmasters_price():
    url = "https://frontendmasters.com/join/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"}

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find only Individual subscription items
        individual_section = soup.find("div", class_="SubscriptionGroup")
        if individual_section:
            plans = individual_section.find_all("div", class_="SubscriptionItem")
            prices = []

            for plan in plans:
                plan_name = plan.find("h3").get_text(strip=True) if plan.find("h3") else "Unknown Plan"
                price = plan.find("em").get_text(strip=True) if plan.find("em") else "Price not found"
                prices.append(f"{plan_name}: {price}")

            return "\n".join(prices)
        else:
            return "Individual pricing section not found."
    else:
        return f"Failed to fetch the page. Status code: {response.status_code}"

def send_email(content):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "FrontendMasters Pricing Update"

    msg.attach(MIMEText(content, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)

if __name__ == "__main__":
    price_info = get_coursera_plus_annual_price()
    send_email(price_info)

