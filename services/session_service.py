import json

from selenium import webdriver

from core.settings import settings
from helpers.logger import get_logger

log = get_logger(__name__)


def load_session(driver: webdriver.Chrome) -> bool:
    session_file = settings.session_file
    if not session_file.is_file():
        return False

    try:
        cookies = json.loads(session_file.read_text(encoding="utf-8"))
        if not cookies:
            return False

        driver.get(settings.url)
        for cookie in cookies:
            sanitized = {key: value for key, value in cookie.items() if value is not None}
            if "expiry" in sanitized:
                sanitized["expiry"] = int(sanitized["expiry"])
            try:
                driver.add_cookie(sanitized)
            except Exception:
                fallback = {
                    key: value
                    for key, value in sanitized.items()
                    if key not in {"sameSite", "storeId"}
                }
                driver.add_cookie(fallback)

        driver.get(settings.url)
        log.info("Session cookies dimuat dari %s", session_file)
        return True
    except Exception as exc:
        log.warning("Gagal memuat session cookies: %s", exc)
        return False


def save_session(driver: webdriver.Chrome) -> bool:
    session_file = settings.session_file
    try:
        cookies = driver.get_cookies()
        session_file.write_text(
            json.dumps(cookies, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
        log.info("Session cookies disimpan ke %s", session_file)
        return True
    except Exception as exc:
        log.warning("Gagal menyimpan session cookies: %s", exc)
        return False
