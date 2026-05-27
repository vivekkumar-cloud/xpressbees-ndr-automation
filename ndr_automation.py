from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
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
PASSWORD = "Tank123@2025"

# ─── URLs ────────────────────────────────────────────────────────────────────
LOGIN_URL = "https://ship.xpressbees.com/users"
NDR_URL   = "https://ship.xpressbees.com/ndr"

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def take_screenshot(driver, name):
    filename = f"screenshot_{name}.png"
    driver.save_screenshot(filename)
    log.info(f"📸 Screenshot saved: {filename}")

def login(driver, wait):
    log.info("Navigating to login page...")
    driver.get(LOGIN_URL)
    time.sleep(3)

    log.info(f"Current URL after load: {driver.current_url}")
    log.info(f"Page title: {driver.title}")
    take_screenshot(driver, "01_login_page")

    # Enter email
    email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
    email_field.clear()
    email_field.send_keys(EMAIL)
    log.info("Email entered.")
    time.sleep(1)

    # Enter password
    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys(PASSWORD)
    log.info("Password entered.")
    time.sleep(1)

    take_screenshot(driver, "02_filled_form")

    # Click Login button
    login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Login')]")
    login_btn.click()
    log.info("Login button clicked. Waiting for redirect...")
    time.sleep(5)

    log.info(f"URL after login click: {driver.current_url}")
    log.info(f"Page title after login: {driver.title}")
    take_screenshot(driver, "03_after_login_click")

    # Wait up to 30s for any redirect away from /users
    for i in range(30):
        current = driver.current_url
        log.info(f"  [{i+1}s] Current URL: {current}")
        if "/users" not in current:
            log.info("✅ Redirected away from login page!")
            break
        time.sleep(1)

    take_screenshot(driver, "04_final_login_state")
    log.info(f"Final URL: {driver.current_url}")

    if "/users" in driver.current_url:
        # Check for error messages on page
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            log.info(f"Page body text snippet: {page_text[:500]}")
        except:
            pass
        raise Exception("Login failed - still on login page after 30 seconds")

    log.info("✅ Login successful!")
    time.sleep(2)

def navigate_to_ndr(driver, wait):
    log.info("Navigating to NDR page...")
    driver.get(NDR_URL)
    time.sleep(3)
    log.info(f"NDR page URL: {driver.current_url}")
    take_screenshot(driver, "05_ndr_page")
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
    time.sleep(4)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")))
    take_screenshot(driver, "06_per_page_500")
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
    take_screenshot(driver, "07_all_selected")

def click_bulk_ndr(driver, wait):
    log.info("Clicking Bulk NDR button...")
    bulk_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fill_bulk_ndr"))
    )
    bulk_btn.click()
    log.info("✅ Bulk NDR button clicked.")
    time.sleep(3)
    take_screenshot(driver, "08_bulk_ndr_panel")

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
    log.info("✅ Remark entered.")
    time.sleep(1)

    take_screenshot(driver, "09_before_submit")

    submit_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'].btn-primary")
    submit_btn.click()
    log.info("✅ Submit clicked!")
    time.sleep(5)
    take_screenshot(driver, "10_after_submit")

def main():
    log.info("=" * 60)
    log.info(f"Xpressbees NDR Automation Started at {datetime.now()}")
    log.info("=" * 60)

    driver = get_driver()
    wait   = WebDriverWait(driver, 30)

    try:
        login(driver, wait)
        navigate_to_ndr(driver, wait)

        initial_count = get_action_required_count(driver)
        log.info(f"📊 Initial Action Required: {initial_count}")

        set_max_per_page(driver, wait)
        select_all_checkboxes(driver, wait)
        click_bulk_ndr(driver, wait)
        submit_reattempt(driver, wait)

        navigate_to_ndr(driver, wait)
        final_count = get_action_required_count(driver)
        log.info(f"📊 Final Action Required: {final_count}")
        log.info("🎉 NDR Automation completed successfully!")

    except Exception as e:
        log.error(f"❌ Error: {e}", exc_info=True)
        take_screenshot(driver, "ERROR_state")
        raise
    finally:
        time.sleep(2)
        driver.quit()
        log.info("Browser closed.")

if __name__ == "__main__":
    main()
