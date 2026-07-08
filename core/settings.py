import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_TEMPLATE_FILE = BASE_DIR / "config.template.json"


def _read_config() -> dict[str, Any]:
    if not CONFIG_FILE.is_file():
        raise FileNotFoundError(
            "config.json tidak ditemukan. Salin config.template.json menjadi config.json lalu isi nilainya."
        )

    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"config.json tidak valid: {exc}") from exc


def _require_str(config: dict[str, Any], key: str) -> str:
    value = str(config.get(key, "")).strip()
    if not value:
        raise EnvironmentError(f"[config] '{key}' wajib diisi di config.json")
    return value


def _optional_str(config: dict[str, Any], key: str, default: str = "") -> str:
    return str(config.get(key, default)).strip()


def _optional_bool(config: dict[str, Any], key: str, default: bool = False) -> bool:
    value = config.get(key, default)
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("true", "1", "yes")


def _optional_int(config: dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(config.get(key, default))
    except (TypeError, ValueError):
        return default


def _resolve_download_dir(config: dict[str, Any]) -> Path:
    raw = _optional_str(config, "download_dir")
    return Path(raw).expanduser().resolve() if raw else Path.home() / "Downloads" / "CoretaxSlips"


@dataclass
class Settings:
    nik: str
    password: str
    url: str
    target_period: str
    tenant_name: Optional[str]
    tenant_npwp: Optional[str]
    download_dir: Path
    chromedriver_path: Optional[str]
    session_file: Path
    browser_headless: bool
    selenium_timeout: int
    captcha_retry: int

    def __post_init__(self):
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def display(self) -> None:
        if getattr(sys, "stdout", None) is None:
            return

        nik_masked = self.nik[:4] + "*" * (len(self.nik) - 4)
        lines = [
            ("URL", self.url),
            ("NIK", nik_masked),
            ("Password", "*" * len(self.password)),
            ("Target Periode", self.target_period),
            ("Tenant Name", self.tenant_name or "-"),
            ("Tenant NPWP", self.tenant_npwp or "-"),
            ("Download Dir", self.download_dir),
            ("ChromeDriver", self.chromedriver_path),
            ("Session File", self.session_file),
            ("Headless", self.browser_headless),
            ("Timeout", f"{self.selenium_timeout}s"),
            ("Captcha Retry", f"{self.captcha_retry}x"),
        ]
        print("─" * 48)
        print("  Coretax DJP — Settings")
        print("─" * 48)
        for label, value in lines:
            print(f"  {label:<16}: {value}")
        print("─" * 48)

    def set_target_period(self, period: str) -> None:
        value = period.strip()
        if value:
            self.target_period = value


def load_settings() -> Settings:
    config = _read_config()
    return Settings(
        nik=_require_str(config, "nik"),
        password=_require_str(config, "password"),
        url=_optional_str(
            config,
            "url",
            "https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login",
        ),
        target_period=_optional_str(config, "target_period", "Januari 2026"),
        tenant_name=_optional_str(config, "tenant_name") or None,
        tenant_npwp=_optional_str(config, "tenant_npwp") or None,
        download_dir=_resolve_download_dir(config),
        chromedriver_path=_optional_str(config, "chromedriver_path") or None,
        session_file=BASE_DIR / ".session" / "coretax_cookies.json",
        browser_headless=_optional_bool(config, "browser_headless", default=False),
        selenium_timeout=_optional_int(config, "selenium_timeout", default=20),
        captcha_retry=_optional_int(config, "captcha_retry", default=5),
    )


settings = load_settings()
