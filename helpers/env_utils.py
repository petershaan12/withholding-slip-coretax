import os
from pathlib import Path


def require_env(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise EnvironmentError(f"[settings] '{key}' wajib diisi di file .env")
    return value


def optional_env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


def bool_env(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).strip().lower() in ("true", "1", "yes")


def int_env(key: str, default: int = 0) -> int:
    try:
        return int(os.getenv(key, str(default)).strip())
    except ValueError:
        return default


def resolve_download_dir() -> Path:
    raw = optional_env("CORETAX_DOWNLOAD_DIR")
    return Path(raw).expanduser().resolve() if raw else Path.home() / "Downloads" / "CoretaxSlips"
