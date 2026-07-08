from helpers.logger import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


def prompt_target_period(settings) -> None:
    default_period = settings.target_period
    entered = input(f"Masukkan periode bulan [{default_period}]: ").strip()
    settings.set_target_period(entered or default_period)


def main() -> None:
    run_app(prompt_period=True, prompt_before_close=True)


def run_app(
    target_period: str | None = None,
    *,
    prompt_period: bool = False,
    prompt_before_close: bool = False,
) -> int:
    from core.settings import settings
    from services.auth_service import login
    from services.download_service import search_and_download, wait_for_downloads
    from services.navigation_service import navigate_to_withholding
    from utils.driver_utils import create_driver

    if target_period:
        settings.set_target_period(target_period)
    elif prompt_period:
        prompt_target_period(settings)

    settings.display()

    driver = None
    try:
        driver = create_driver()

        if not login(driver):
            return 1
        if not navigate_to_withholding(driver):
            return 1

        count = search_and_download(driver)

        if count > 0:
            wait_for_downloads()
            log.info("Selesai! %s PDF tersimpan di: %s", count, settings.download_dir)
        else:
            log.warning("Tidak ada file yang didownload.")

        return 0
    except Exception as exc:
        log.error("Error tidak terduga: %s", exc, exc_info=True)
        return 1
    finally:
        if driver:
            if prompt_before_close:
                input("\nTekan Enter untuk menutup browser...")
            driver.quit()
            log.info("Browser ditutup.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        log.error("%s", exc)
        input("\nTekan Enter untuk keluar...")
