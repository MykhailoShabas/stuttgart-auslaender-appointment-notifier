# ---------------------------------------------------------------------------------------------
# Name: script to check available appointments on the Stuttgart Immigration Office website.
#
# Description: This script provides functionality to check for available appointments
#              on the website of Stuttgart Immigration Office. It looks for service point
#              "Ausländerbehörde - Servicepoint" and the option "Übertragung bestehender
#              Aufenthaltstitel auf neuen Nationalpass (sog. Übertrag) (1 Person)".
#              The 'ntfy' app is used to send notifications to your phone when an appointment
#              is available ('ntfy' app installation is required).
#
# Author: Mykhailo Shabas
# Changelog:
#     Version: 1.3
#        Changed by: Mykhailo Shabas
#        Date: 16.04.2025
# ---------------------------------------------------------------------------------------------

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Defaults
DEBUG = False
WEBSITE_URL = "https://stuttgart.konsentas.de/form/7/?signup_new=1"

# Selenium WebDriver settings
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

def appointments_available():
    """Check the website for available appointments.

    Returns:
        bool: True if appointments are available, False otherwise.
    """
    try:
        # Open the website
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(WEBSITE_URL)
        wait = WebDriverWait(driver, 10)

        # **Step 1: Click "Ausländerbehörde - Servicepoint"**
        servicepoint = wait.until(EC.element_to_be_clickable((By.ID, "collapse-dep-12")))
        servicepoint.click()
        if DEBUG: print("✅ Clicked 'Ausländerbehörde - Servicepoint'")

        # **Step 2: Click the "Optionen" dropdown**
        dropdown_button = wait.until(EC.element_to_be_clickable((By.ID, "process-options-dropdown-12_57")))
        dropdown_button.click()
        if DEBUG: print("✅ Clicked 'Optionen' dropdown")
        dropdown_list = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dropdown-menu.show")))
        if DEBUG: print("✅ Dropdown menu is now visible")

        # Step 3: Select "1 Person" with "30 Minuten"
        option_1_person = wait.until(EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'dropdown-menu')]/li/a[div/span[text()='1 Person'] and div/span[contains(text(), '30 Minuten')]]")))
        option_1_person.click()
        if DEBUG: print("✅ Selected '1 Person' with '30 Minuten'")

        # Step 4: Click "Weiter" button
        weiter_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn_formcontroll_next')]")))
        driver.execute_script("arguments[0].click();", weiter_button)
        if DEBUG: print("✅ Clicked 'Weiter' button")

        # Step 5: Wait until the page is loaded
        wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@id='bertragungbestehenderaufenthaltstitelaufneuennationalpasssogbertrag1person']")))
        if DEBUG: print("✅ Page loaded: 'Ihre gewählte Leistung' found")

        if DEBUG:
            driver.save_screenshot("docs\debug-servicepoint-1.png")
            print("📸 Screenshot saved: debug-servicepoint-1.png")

        # Step 6: Click the second "Weiter" button
        weiter_buttons = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "btn_formcontroll_next")))
        weiter_buttons[-1].click()
        if DEBUG: print("✅ Clicked the second 'Weiter' button")

        wait.until(EC.any_of(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Keine verfügbaren Termine!')]")),
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Bitte wählen Sie ein Datum')]"))))

        if DEBUG:
            driver.save_screenshot("docs\debug-servicepoint-2.png")
            print("📸 Screenshot saved: debug-servicepoint-2.png")

        # Try to find text "Keine verfügbaren Termine" or "Bitte wählen Sie ein Datum"
        no_appointments = driver.find_elements(By.XPATH, "//*[contains(text(), 'Keine verfügbaren Termine!')]")
        choose_date = driver.find_elements(By.XPATH, "//*[contains(text(), 'Bitte wählen Sie ein Datum')]")

        if choose_date:
            print("🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨")
            print("✅✅✅ Appointments available ✅✅✅")
            driver.save_screenshot("date_selection.png")
            print("📸 Screenshot saved: date_selection.png")
            return True
        elif no_appointments:
            print("⚠️ No available appointments.")
            return False
        else:
            print("❌ ERROR: Neither 'Keine verfügbaren Termine' nor 'Bitte wählen Sie ein Datum' found.")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        driver.quit()

def main():
    print("💻 Executing script...")
    if appointments_available():
        # Send notification to your phone using ntfy app
        topic = "servicepoint_stuttgart_immigration_office"
        title = "Servicepoint - Stuttgart Immigration Office"
        message = "\n✅ Appointments available \n✅ Übertragung bestehender Aufenthaltstitel auf neuen Nationalpass (sog. Übertrag) (1 Person) \n✅ Book your appointment now!"
        requests.post(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"), headers={"Title": title, "Priority": "high"})
        print("✅ Notification was sent")

if __name__ == "__main__":
    main()
