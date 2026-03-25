import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.settings import settings
from helpers.logger import get_logger
from services.captcha_service import refresh_captcha, solve_captcha

log = get_logger(__name__)


def login(driver: webdriver.Chrome) -> bool:
    wait = WebDriverWait(driver, settings.selenium_timeout)

    log.info("Membuka %s ...", settings.url)
    driver.get(settings.url)
    time.sleep(2)

    for attempt in range(1, settings.captcha_retry + 1):
        log.info("Percobaan login ke-%s/%s ...", attempt, settings.captcha_retry)
        try:
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

            captcha_text = solve_captcha(driver, "#dntCaptchaImg")
            if not captcha_text:
                log.warning("OCR captcha kosong, refresh captcha...")
                refresh_captcha(driver)
                continue

            cap_el = driver.find_element(By.ID, "DNTCaptchaInputText")
            cap_el.clear()
            cap_el.send_keys(captcha_text)

            driver.find_element(
                By.CSS_SELECTOR,
                "button[type='submit'], input[type='submit'], .btn-login",
            ).click()
            time.sleep(3)

            page = driver.page_source.lower()
            if any(text in page for text in ("captcha salah", "invalid captcha", "login gagal")):
                log.warning("Login ditolak, coba lagi...")
                refresh_captcha(driver)
                continue

            if "dashboard" in driver.current_url.lower() or is_logged_in(driver):
                log.info("Login berhasil.")
                return True

        except TimeoutException:
            log.warning("Timeout pada percobaan %s.", attempt)
        except NoSuchElementException as exc:
            log.error("Elemen login tidak ditemukan: %s", exc)
            break

    log.error("Semua percobaan login gagal.")
    return False


def is_logged_in(driver: webdriver.Chrome) -> bool:
    try:
        driver.find_element(By.CSS_SELECTOR, ".navbar")
        driver.find_element(By.CSS_SELECTOR, ".image-content")
        return True
    except NoSuchElementException:
        return False
