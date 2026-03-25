import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.settings import settings
from helpers.logger import get_logger

log = get_logger(__name__)


def navigate_to_withholding(driver: webdriver.Chrome) -> bool:
    wait = WebDriverWait(driver, settings.selenium_timeout)
    log.info("Navigasi ke eBupot -> Bukti Potong Saya ...")

    try:
        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@title, 'eBupot') and contains(@class, 'dropdown-toggle')]",
                )
            )
        ).click()
        time.sleep(1.2)

        wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@href, '/withholding-slips-portal') and contains(text(), 'Bukti Potong Saya')]",
                )
            )
        ).click()
        time.sleep(2)

        log.info("Halaman Bukti Potong Saya terbuka.")
        return True
    except TimeoutException:
        log.error("Gagal navigasi ke menu eBupot. Cek selector XPath.")
        return False
