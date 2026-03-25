import base64
from io import BytesIO

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from core.settings import settings


def element_to_base64(driver: webdriver.Chrome, selector: str) -> str:
    """Screenshot elemen dan kembalikan sebagai data URL base64."""
    el = driver.find_element(By.CSS_SELECTOR, selector)
    img = Image.open(BytesIO(el.screenshot_as_png))
    buf = BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def create_driver() -> webdriver.Chrome:
    opts = Options()
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
    service = Service(settings.chromedriver_path)
    return webdriver.Chrome(service=service, options=opts)
