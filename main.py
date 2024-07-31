import json
import os
import time
import logging
import re
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_credentials():
    logging.info("Getting credentials")
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            logging.info("Credentials loaded from token.json")
        except Exception as e:
            logging.error(f"Error reading credentials: {e}")
            creds = None

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                logging.info("Credentials refreshed")
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret_oauth.json', SCOPES)
                creds = flow.run_local_server(port=0)
                logging.info("New credentials obtained from client secrets")
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                logging.info("New credentials saved to token.json")
        except Exception as e:
            logging.error(f"Error during authentication: {e}")
            creds = None

    return creds

def get_otp_from_gmail(creds, start_time, max_retries=20):
    logging.info("Starting to get OTP from Gmail")
    service = build('gmail', 'v1', credentials=creds)
    last_message = None

    for attempt in range(max_retries):
        logging.info(f"Attempt {attempt + 1} of {max_retries}")
        try:
            results = service.users().messages().list(
                userId='me',
                q='from:otp@hackeru.com'
            ).execute()
        except Exception as e:
            logging.error(f"Error querying Gmail: {e}")
            time.sleep(10)
            continue

        if not results.get('messages', []):
            logging.info('No OTP email found yet. Retrying in 10 seconds...')
            time.sleep(10)
            continue

        for msg in results['messages']:
            try:
                message = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = message['snippet']
                internal_date = int(message['internalDate']) / 1000  # internalDate is in milliseconds
                email_time = datetime.fromtimestamp(internal_date, tz=timezone.utc)

                if email_time > start_time:
                    otp_match = re.search(r'Your OTP Code is (\d{6})', snippet)
                    if otp_match:
                        logging.info(f"Found OTP code: {otp_match.group(1)}")
                        return otp_match.group(1)
                    else:
                        logging.info(f"No OTP match found in this email: {snippet}")
                        last_message = snippet
            except Exception as e:
                logging.error(f"Error reading message: {e}")

    logging.error('Error: No OTP emails found after retries.')
    if last_message:
        print(f"Last email snippet: {last_message}")
    return None

def main():
    logging.info("Script started")
    start_time = datetime.now(timezone.utc)
    creds = get_credentials()
    if not creds:
        logging.error("Failed to obtain Gmail credentials.")
        return

    credentials_file = "credentials.json"
    use_saved = False

    if os.path.exists(credentials_file):
        try:
            with open(credentials_file, 'r') as f:
                credentials_data = json.load(f)
                if credentials_data.get('username') and credentials_data.get('password'):
                    username = credentials_data.get('username')
                    password = credentials_data.get('password')
                    use_saved = input(f"Use saved credentials for {username}? (y/n): ").lower() == 'y'
                    logging.info(f"Using saved credentials: {use_saved}")
        except Exception as e:
            logging.error(f"Error reading credentials file: {e}")

    if not use_saved:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        try:
            with open(credentials_file, 'w') as f:
                json.dump({'username': username, 'password': password}, f)
                logging.info("New credentials saved to credentials.json")
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")

    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        logging.info("WebDriver initialized")
    except Exception as e:
        logging.error(f"Error initializing WebDriver: {e}")
        return

    try:
        driver.get('https://hackeru.priza.net/')
        logging.info("Navigated to hackeru.priza.net")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        logging.info("Username field is present")

        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        logging.info("Login form submitted")

        WebDriverWait(driver, 10).until(lambda d: d.current_url != "https://hackeru.priza.net/")
        logging.info("Login successful, URL changed")
    except TimeoutException:
        logging.error("Login page did not load in time.")
        driver.quit()
        return
    except Exception as e:
        logging.error(f"Error during login process: {e}")
        driver.quit()
        return

    try:
        wait = WebDriverWait(driver, 60)
        wait.until(lambda d: d.current_url == "https://hackeru.priza.net/default.aspx?action=otp")
        logging.info("OTP page loaded")
        otp_code = get_otp_from_gmail(creds, start_time)

        if otp_code:
            for i, digit in enumerate(otp_code):
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, f"digit-{i + 1}"))).send_keys(digit)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'ctl00_PageBody_OTP_Button1'))).click()
            logging.info("OTP code entered and submitted")

            # Continue using the same WebDriver session
            logging.info("Authenticated session, performing further tasks")
            driver.get('https://hackeru.priza.net/some_authenticated_page')
            logging.info("Navigated to authenticated page")

        else:
            logging.error("Failed to retrieve OTP code.")
    except TimeoutException:
        logging.error("OTP page did not load in time.")
    except NoSuchElementException:
        logging.error("Unable to locate OTP button.")
    except Exception as e:
        logging.error(f"Error during OTP handling: {e}")
    finally:
        logging.info("Selenium WebDriver session is still active")
        # driver.quit()  # Comment this out to keep the session open

    logging.info("Authenticated session is open in the current WebDriver")

if __name__ == '__main__':
    main()
