import platform
from pathlib import Path
from shutil import which

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver

from core.settings import settings


def _resolve_chrome_binary() -> str | None:
    candidates: list[str] = []

    if platform.system() == "Darwin":
        candidates.extend(
            [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            ]
        )
    elif platform.system() == "Windows":
        candidates.extend(
            [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
        )

    for name in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        found = which(name)
        if found:
            candidates.append(found)

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate

    return None


def create_driver() -> ChromeDriver:
    opts = Options()
    chrome_binary = _resolve_chrome_binary()
    if chrome_binary:
        opts.binary_location = chrome_binary

    if settings.browser_headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--lang=id-ID")
    opts.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(settings.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "safebrowsing.enabled": True,
        },
    )
    return ChromeDriver(options=opts)
