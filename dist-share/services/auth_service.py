import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.settings import settings
from helpers.logger import get_logger
from services.session_service import load_session, save_session

log = get_logger(__name__)


def login(driver: webdriver.Chrome) -> bool:
    wait = WebDriverWait(driver, settings.selenium_timeout)

    log.info("Membuka %s ...", settings.url)
    driver.get(settings.url)
    time.sleep(2)

    if load_session(driver) and is_logged_in(driver):
        log.info("Session lama masih valid.")
        if not ensure_target_tenant(driver):
            return False
        save_session(driver)
        return True

    try:
        if is_logged_in(driver):
            log.info("Session sudah login.")
            if not ensure_target_tenant(driver):
                return False
            save_session(driver)
            return True

        nik_el = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input[name='username'], input[id*='nik'], input[type='text']",
                )
            )
        )
        nik_el.clear()
        nik_el.send_keys(settings.nik)

        pwd_el = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        pwd_el.clear()
        pwd_el.send_keys(settings.password)

        log.info(
            "Username dan password sudah diisi. Selesaikan ALTCHA dan klik login langsung di browser."
        )
        wait = WebDriverWait(driver, settings.selenium_timeout * 30)
        wait.until(lambda current_driver: is_logged_in(current_driver))
        log.info("Login berhasil.")

        if not ensure_target_tenant(driver):
            return False
        save_session(driver)
        return True
    except TimeoutException:
        log.error("Timeout menunggu login manual selesai.")
        return False


def ensure_target_tenant(driver: webdriver.Chrome) -> bool:
    if not settings.tenant_name and not settings.tenant_npwp:
        return True

    current_name, current_npwp = get_current_identity(driver)
    if tenant_matches(current_name, current_npwp):
        log.info("Tenant target sudah aktif: %s / %s", current_name or "-", current_npwp or "-")
        return True

    wait = WebDriverWait(driver, settings.selenium_timeout)
    try:
        profile_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".tw-profilebtn-wide"))
        )
        profile_button.click()
        time.sleep(0.8)

        search_inputs = driver.find_elements(By.CSS_SELECTOR, ".tw-pm-search-input")
        if search_inputs and settings.tenant_npwp:
            search_input = search_inputs[0]
            search_input.clear()
            search_input.send_keys(settings.tenant_npwp)
            time.sleep(0.8)
        elif search_inputs and settings.tenant_name:
            search_input = search_inputs[0]
            search_input.clear()
            search_input.send_keys(settings.tenant_name)
            time.sleep(0.8)

        target_button = find_target_tenant_button(driver)
        if target_button is None:
            log.error("Tenant target tidak ditemukan di daftar profil.")
            return False

        if "is-active" in (target_button.get_attribute("class") or ""):
            log.info("Tenant target sudah aktif.")
            return True

        target_label = target_button.text.strip().replace("\n", " | ")
        log.info("Mengganti tenant ke: %s", target_label)
        target_button.click()

        wait.until(lambda current_driver: tenant_matches(*get_current_identity(current_driver)))
        time.sleep(1.5)
        log.info("Tenant berhasil diganti.")
        return True
    except TimeoutException:
        log.error("Timeout saat mengganti tenant.")
        return False


def find_target_tenant_button(driver: webdriver.Chrome):
    buttons = driver.find_elements(By.CSS_SELECTOR, ".tw-pm-imp-item")
    for button in buttons:
        name = ""
        npwp = ""
        try:
            name = button.find_element(By.CSS_SELECTOR, ".tw-pm-imp-name").text.strip()
        except NoSuchElementException:
            pass
        try:
            npwp = button.find_element(By.CSS_SELECTOR, ".tw-pm-imp-sub").text.strip()
        except NoSuchElementException:
            pass

        if tenant_matches(name, npwp):
            return button

    return None


def get_current_identity(driver: webdriver.Chrome) -> tuple[str, str]:
    try:
        name = driver.find_element(By.CSS_SELECTOR, ".tw-profile-name").text.strip()
    except NoSuchElementException:
        name = ""

    try:
        npwp = driver.find_element(By.CSS_SELECTOR, ".tw-profile-npwp").text.strip()
    except NoSuchElementException:
        npwp = ""

    return name, npwp


def tenant_matches(name: str, npwp: str) -> bool:
    if settings.tenant_name and settings.tenant_name.casefold() != name.casefold():
        return False
    if settings.tenant_npwp and settings.tenant_npwp != npwp:
        return False
    return bool(settings.tenant_name or settings.tenant_npwp)


def is_logged_in(driver: webdriver.Chrome) -> bool:
    current_url = driver.current_url.lower()
    if "dashboard" in current_url:
        return True

    selectors = [
        ".navbar",
        ".image-content",
        ".tw-profilebtn-wide",
        "a[title*='eBupot']",
        "a[href*='withholding-slips-portal']",
    ]

    for selector in selectors:
        try:
            driver.find_element(By.CSS_SELECTOR, selector)
            return True
        except NoSuchElementException:
            continue

    return False
