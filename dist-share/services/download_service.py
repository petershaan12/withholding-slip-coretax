import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.settings import settings
from helpers.logger import get_logger

log = get_logger(__name__)


def search_and_download(driver: webdriver.Chrome) -> int:
    wait = WebDriverWait(driver, settings.selenium_timeout)
    downloaded = 0

    log.info("Mencari slip periode: %s ...", settings.target_period)

    try:
        click_dropdown_option(driver, wait, "JenisBuktiPotong", "pr_id_4_list", "BP A1")

        wait.until(EC.element_to_be_clickable((By.ID, "search"))).click()
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .p-datatable-tbody tr")
        if not rows:
            time.sleep(2)
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .p-datatable-tbody tr")
        if not rows:
            log.warning("Tidak ada data ditemukan.")
            return 0

        try:
            click_dropdown_option(
                driver,
                wait,
                "filterIncomePeriodCodeEnd",
                "pr_id_11_list",
                settings.target_period,
            )
        except Exception as exc:
            log.warning("Tidak bisa filter Masa Akhir Periode: %s", exc)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr, .p-datatable-tbody tr")
        if not rows:
            log.warning("Tidak ada data setelah filter.")
            return 0

        col_idx = find_column_index(driver, "Masa Akhir Periode Penghasilan")
        if col_idx is None:
            log.warning("Kolom 'Masa Akhir Periode Penghasilan' tidak ditemukan.")
            return 0

        log.info("Ditemukan %s baris.", len(rows))

        for idx, row in enumerate(rows, start=1):
            try:
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if not cells or col_idx >= len(cells):
                    continue

                masa_akhir = cells[col_idx].text.strip().lower()
                log.info("Baris %s | Masa Akhir: %s", idx, masa_akhir)

                if settings.target_period.lower() not in masa_akhir:
                    continue

                log.info("Download baris %s ...", idx)
                download_button = find_download_button(row, driver, wait)
                download_button.click()
                downloaded += 1
                time.sleep(2)

            except Exception as exc:
                log.warning("Gagal download baris %s: %s", idx, exc)

    except TimeoutException:
        log.error("Timeout saat pencarian/download.")

    return downloaded


def wait_for_downloads(timeout: int = 60) -> bool:
    log.info("Menunggu download selesai di: %s", settings.download_dir)
    end_time = time.time() + timeout

    while time.time() < end_time:
        pending = list(settings.download_dir.glob("*.crdownload"))
        if not pending:
            log.info("Semua file selesai didownload.")
            return True

        log.info("Masih %s file dalam proses...", len(pending))
        time.sleep(2)

    log.warning("Timeout download. Cek folder secara manual.")
    return False


def click_dropdown_option(
    driver: webdriver.Chrome,
    wait: WebDriverWait,
    dropdown_id: str,
    list_id: str,
    label: str,
) -> None:
    dropdown = wait.until(EC.element_to_be_clickable((By.ID, dropdown_id)))

    try:
        trigger = driver.find_element(
            By.XPATH,
            f"//div[@id='{dropdown_id}']//div[contains(@class, 'p-dropdown-trigger')]",
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", trigger)
        trigger.click()
    except NoSuchElementException:
        dropdown.click()

    time.sleep(1)

    option_list = wait.until(EC.presence_of_element_located((By.ID, list_id)))
    option_list.find_element(
        By.XPATH,
        f".//li[contains(@aria-label, '{label}') or contains(., '{label}')]",
    ).click()
    time.sleep(1)


def find_column_index(driver: webdriver.Chrome, header_text: str) -> int | None:
    headers = driver.find_elements(By.CSS_SELECTOR, "table thead th, .p-datatable-thead th")
    for index, header in enumerate(headers):
        if header_text in header.text:
            return index
    return None


def find_download_button(
    row,
    driver: webdriver.Chrome,
    wait: WebDriverWait,
):
    try:
        return row.find_element(
            By.CSS_SELECTOR,
            "button[title*='Download'], .btn-pdf, a[href*='.pdf'], #DownloadButton",
        )
    except NoSuchElementException:
        row.click()
        time.sleep(1.5)
        return wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[title*='Download'], .btn-download")
            )
        )
