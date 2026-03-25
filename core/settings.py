from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from helpers.env_utils import (
    bool_env,
    int_env,
    optional_env,
    require_env,
    resolve_download_dir,
)

# Load .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Settings 
@dataclass
class Settings:
    # Kredensial
    nik: str
    password: str

    # Target
    url: str
    target_period: str

    # Paths
    download_dir: Path
    chromedriver_path: str

    # Selenium
    browser_headless: bool
    selenium_timeout: int
    captcha_retry: int

    # Qwen / DashScope
    qwen_apikey: str
    dashscope_base_url: str = field(default="https://dashscope-intl.aliyuncs.com/compatible-mode/v1")
    dashscope_model: str = field(default="qwen3-vl-flash-2026-01-22")

    def __post_init__(self):
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def display(self) -> None:
        """Tampilkan ringkasan settings (kredensial disensor)."""
        nik_masked = self.nik[:4] + "*" * (len(self.nik) - 4)
        lines = [
            ("URL",            self.url),
            ("NIK",            nik_masked),
            ("Password",       "*" * len(self.password)),
            ("Target Periode", self.target_period),
            ("Download Dir",   self.download_dir),
            ("ChromeDriver",   self.chromedriver_path),
            ("Headless",       self.browser_headless),
            ("Timeout",        f"{self.selenium_timeout}s"),
            ("Captcha Retry",  f"{self.captcha_retry}x"),
            ("OCR Model",      self.dashscope_model),
        ]
        print("─" * 48)
        print("  Coretax DJP — Settings")
        print("─" * 48)
        for label, value in lines:
            print(f"  {label:<16}: {value}")
        print("─" * 48)


# ── Singleton ─────────────────────────────────────────────────────────────────

settings = Settings(
    nik=require_env("CORETAX_NIK"),
    password=require_env("CORETAX_PASSWORD"),
    url=optional_env(
        "CORETAX_URL",
        "https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login",
    ),
    target_period=optional_env("CORETAX_TARGET_PERIOD", "Januari 2026"),
    download_dir=resolve_download_dir(),
    chromedriver_path=optional_env("CHROMEDRIVER_PATH", r"C:\tools\chromedriver.exe"),
    browser_headless=bool_env("BROWSER_HEADLESS", default=False),
    selenium_timeout=int_env("SELENIUM_TIMEOUT", default=20),
    captcha_retry=int_env("CAPTCHA_RETRY", default=5),
    qwen_apikey=require_env("QWEN_APIKEY"),
    dashscope_base_url=optional_env(
        "DASHSCOPE_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ),
    dashscope_model=optional_env("DASHSCOPE_MODEL", "qwen3-vl-flash-2026-01-22"),
)
