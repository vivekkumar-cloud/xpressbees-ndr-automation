from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import logging
from datetime import datetime

# ─── Logging Setup ───────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("ndr_automation.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─── Credentials ─────────────────────────────────────────────────────────────
EMAIL    = "Exyte124@gmail.com"
PASSWORD = "Noida2024@pax"

# ─── URLs ────────────────────────────────────────────────────────────────────
LOGIN_URL = "https://ship.xpressbees.com/users"
NDR_URL   = "https://ship.xpressbees.com/ndr"

def get_driver():
    options = Options()
    options.add_argument("--headless")               # No browser window (GitHub Actions)
    options.add_argument("--no-sandbox")             # Required for Linux CI
    options.add_argument("--disable-dev-shm-usage")  # Required for Linux CI
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    return driver

def login(driver, wait):
    log.info("Navigating to login page...")
    driver.get(LOGIN_URL)
    time.sleep(2)

    email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    email_field.clear()
    email_field.send_keys(EMAIL)
    log.info("Email entered.")

    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(PASSWORD)
    log.info("Password entered.")

    login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    login_btn.click()
    log.info("Login button clicked. Waiting for dashboard...")

    wait.until(EC.url_contains("/dash"))
    log.info("✅ Login successful! Dashboard loaded.")
    time.sleep(2)

def navigate_to_ndr(driver, wait):
    log.info("Navigating to NDR page...")
    driver.get(NDR_URL)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
    log.info("✅ NDR page loaded.")
    time.sleep(2)

def get_action_required_count(driver):
    try:
        tab = driver.find_element(By.XPATH, "//button[contains(text(),'Action Required')]")
        return tab.text.strip()
    except:
        return "N/A"

def set_max_per_page(driver, wait):
    log.info("Setting per-page to 500 (max)...")
    per_page_select = wait.until(
        EC.presence_of_element_located((By.NAME, "per_page"))
    )
    select = Select(per_page_select)
    select.select_by_value("500")
    log.info("Per-page set to 500. Waiting for page reload...")
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
    log.info("✅ Page reloaded with max entries.")
    time.sleep(2)

def select_all_checkboxes(driver, wait):
    log.info("Selecting all checkboxes...")
    select_all = wait.until(
        EC.element_to_be_clickable((By.ID, "select_all_checkboxes"))
    )
    if not select_all.is_selected():
        select_all.click()
        log.info("✅ Select-all checkbox clicked.")
    else:
        log.info("Select-all already checked.")
    time.sleep(2)

def click_bulk_ndr(driver, wait):
    log.info("Clicking Bulk NDR button...")
    bulk_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fill_bulk_ndr"))
    )
    bulk_btn.click()
    log.info("✅ Bulk NDR button clicked. Waiting for side panel...")
    time.sleep(2)

def submit_reattempt(driver, wait):
    log.info("Selecting Re-Attempt action...")

    action_select = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "select#choose.form-control"))
    )
    select = Select(action_select)
    select.select_by_visible_text("Re-Attempt")
    log.info("✅ Re-Attempt selected.")
    time.sleep(1)

    remark_field = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[name='remarks']"))
    )
    remark_field.clear()
    remark_field.send_keys("Reattempt")
    log.info("✅ Remark entered: Reattempt")
    time.sleep(1)

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'].btn-primary")
    submit_btn.click()
    log.info("✅ Submit button clicked. NDR action submitted!")
    time.sleep(4)

def main():
    log.info("=" * 60)
    log.info(f"Xpressbees NDR Automation Started at {datetime.now()}")
    log.info("=" * 60)

    driver = get_driver()
    wait   = WebDriverWait(driver, 30)

    try:
        # Step 1: Login
        login(driver, wait)

        # Step 2: Go to NDR page
        navigate_to_ndr(driver, wait)

        # Step 3: Check initial count
        initial_count = get_action_required_count(driver)
        log.info(f"📊 Initial Action Required count: {initial_count}")

        # Step 4: Set per-page to max (500)
        set_max_per_page(driver, wait)

        # Step 5: Select all
        select_all_checkboxes(driver, wait)

        # Step 6: Click Bulk NDR
        click_bulk_ndr(driver, wait)

        # Step 7: Re-Attempt + Remark + Submit
        submit_reattempt(driver, wait)

        # Step 8: Final count
        navigate_to_ndr(driver, wait)
        final_count = get_action_required_count(driver)
        log.info(f"📊 Final Action Required count: {final_count}")
        log.info("🎉 NDR Automation completed successfully!")

    except Exception as e:
        log.error(f"❌ Error occurred: {e}", exc_info=True)
        raise  # Re-raise so GitHub Actions marks run as FAILED
    finally:
        time.sleep(2)
        driver.quit()
        log.info("Browser closed.")

if __name__ == "__main__":
    main()
