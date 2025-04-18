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

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re

def get_coursera_plus_annual_price():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://www.coursera.org/courseraplus")

        # Wait up to 15 seconds for any elements that might contain a dollar sign
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '$')]"))
        )

        # Now get all visible text on the page
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Use regex to search for patterns like "$399/year", "$59/month", etc.
        matches = re.findall(r"\$\d{2,4}\/year", page_text, re.IGNORECASE)
        if matches:
            return f"Coursera Plus Annual: {matches[0]}"
        
        return "Coursera Plus Annual price not found."
    except Exception as e:
        return f"Error occurred: {e}"
    finally:
        driver.quit()

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
    msg["Subject"] = "Coursera Pricing Update"

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
    print(price_info)
    send_email(price_info)

