from core.settings import settings
from helpers.logger import configure_logging, get_logger
from services.auth_service import login
from services.download_service import search_and_download, wait_for_downloads
from services.navigation_service import navigate_to_withholding
from utils.driver_utils import create_driver

configure_logging()
log = get_logger(__name__)


def main() -> None:
    settings.display()

    driver = None
    try:
        driver = create_driver()

        if not login(driver):
            return
        if not navigate_to_withholding(driver):
            return

        count = search_and_download(driver)

        if count > 0:
            wait_for_downloads()
            log.info("Selesai! %s PDF tersimpan di: %s", count, settings.download_dir)
        else:
            log.warning("Tidak ada file yang didownload.")

    except Exception as exc:
        log.error("Error tidak terduga: %s", exc, exc_info=True)
    finally:
        if driver:
            input("\nTekan Enter untuk menutup browser...")
            driver.quit()
            log.info("Browser ditutup.")


if __name__ == "__main__":
    main()
