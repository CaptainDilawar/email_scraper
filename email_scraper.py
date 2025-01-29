import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)

# User inputs
site = input("Enter site (e.g., instagram.com): ")
industry = input("Enter industry (e.g., real estate): ")
state = input("Enter state (e.g., Alabama): ")

# Google search query
query = f'site:{site} "{industry}" "{state}" "@gmail.com"'
intext = f'intext:@gmail.com "{industry}" "{state}" inurl:contact'

# Navigate to Google
driver.get("https://www.google.com")
driver.maximize_window()
def extract_it(prompt):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        search_box.clear()
        search_box.send_keys(prompt)
        search_box.send_keys(Keys.RETURN)
        print("Please solve the CAPTCHA if it appears.")
        time.sleep(10)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        results = driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc")
        data = []

        partial_email_pattern = r"[A-Za-z0-9._%+-]+@gmail\.com"

        for result in results:
            title = result.find_element(By.CSS_SELECTOR, "h3").text
            link = result.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            description = result.find_element(By.CSS_SELECTOR, ".VwiC3b").text

            # Find emails in the description FIRST
            emails = re.findall(partial_email_pattern, description)
            if prompt == query:
                try:
                    response = requests.get(link)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_content = soup.get_text()

                    # Add emails found on the page to the list (avoid duplicates)
                    for email in re.findall(partial_email_pattern, page_content):
                        if email not in emails:  # Check for duplicates
                            emails.append(email)
                except requests.exceptions.RequestException as e:
                    print(f"Error accessing {link}: {e}")

            email_list = ", ".join(emails) if emails else "No email found"
            data.append({"Title": title, "Link": link, "Description": description, "Emails": email_list})

        return data

    except Exception as e:
        print("Error:", e)
        return []
# Extract data using query and intext
try:
    data_intext = extract_it(intext)
    data_query = extract_it(query)
    data = data_query + data_intext
    df = pd.DataFrame(data)
    filename = f"google_results_with_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()