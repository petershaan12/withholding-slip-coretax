import json
import logging
import sys
import threading
from pathlib import Path
from tkinter import END, StringVar, Text, Tk, filedialog, messagebox
from tkinter import ttk


APP_TITLE = "Coretax Slip Downloader"
DEFAULT_URL = "https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login"


def app_dir() -> Path:
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent


BASE_DIR = app_dir()
CONFIG_FILE = BASE_DIR / "config.json"
CONFIG_TEMPLATE_FILE = BASE_DIR / "config.template.json"


DEFAULT_CONFIG = {
    "nik": "",
    "password": "",
    "url": DEFAULT_URL,
    "target_period": "Januari 2026",
    "tenant_name": "",
    "tenant_npwp": "",
    "download_dir": "",
    "chromedriver_path": "",
    "browser_headless": False,
    "selenium_timeout": 20,
    "captcha_retry": 5,
}


def load_config() -> dict:
    if CONFIG_FILE.is_file():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_CONFIG, **data}
        except json.JSONDecodeError:
            messagebox.showwarning(APP_TITLE, "config.json tidak valid. Form akan memakai nilai default.")

    if CONFIG_TEMPLATE_FILE.is_file():
        try:
            data = json.loads(CONFIG_TEMPLATE_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_CONFIG, **data}
        except json.JSONDecodeError:
            pass

    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class TkLogHandler(logging.Handler):
    def __init__(self, root: Tk, widget):
        super().__init__()
        self.root = root
        self.widget = widget
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))

    def emit(self, record: logging.LogRecord) -> None:
        message = self.format(record)
        self.root.after(0, self._append, message)

    def _append(self, message: str) -> None:
        self.widget.configure(state="normal")
        self.widget.insert(END, message + "\n")
        self.widget.see(END)
        self.widget.configure(state="disabled")


class CoretaxApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title(APP_TITLE)
        self.root.geometry("760x620")
        self.root.minsize(680, 560)

        self.config_data = load_config()
        self.vars = {
            "nik": StringVar(value=self.config_data.get("nik", "")),
            "password": StringVar(value=self.config_data.get("password", "")),
            "target_period": StringVar(value=self.config_data.get("target_period", "Januari 2026")),
            "tenant_name": StringVar(value=self.config_data.get("tenant_name", "")),
            "tenant_npwp": StringVar(value=self.config_data.get("tenant_npwp", "")),
            "download_dir": StringVar(value=self.config_data.get("download_dir", "")),
            "chromedriver_path": StringVar(value=self.config_data.get("chromedriver_path", "")),
        }

        self.start_button = None
        self.status_var = StringVar(value="Siap")
        self._build_ui()
        self._setup_logging()

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=(18, 16, 18, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ttk.Label(header, text="Coretax Slip Downloader", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.status_var).grid(row=1, column=0, sticky="w", pady=(4, 0))

        body = ttk.Frame(self.root, padding=(18, 8, 18, 12))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(1, weight=1)
        body.rowconfigure(8, weight=1)

        self._entry(body, "NIK", "nik", 0)
        self._entry(body, "Password", "password", 1, show="*")
        self._entry(body, "Periode", "target_period", 2)
        self._entry(body, "Tenant Name", "tenant_name", 3)
        self._entry(body, "Tenant NPWP", "tenant_npwp", 4)
        self._path_entry(body, "Download Folder (opsional)", "download_dir", 5, self._browse_download_dir)
        self._path_entry(body, "ChromeDriver Path (opsional)", "chromedriver_path", 6, self._browse_chromedriver)

        action_bar = ttk.Frame(body)
        action_bar.grid(row=7, column=0, columnspan=3, sticky="ew", pady=(14, 10))
        action_bar.columnconfigure(0, weight=1)

        ttk.Label(action_bar, text="Kosongkan Download Folder untuk default ke Downloads\\CoretaxSlips. Kosongkan ChromeDriver Path kecuali diminta IT.").grid(row=0, column=0, sticky="w")
        self.start_button = ttk.Button(action_bar, text="Mulai Download", command=self.start_download)
        self.start_button.grid(row=0, column=1, sticky="e", padx=(12, 0))

        log_frame = ttk.LabelFrame(body, text="Log Proses", padding=8)
        log_frame.grid(row=8, column=0, columnspan=3, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = Text(log_frame, height=12, wrap="word", state="disabled")
        self.log_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _entry(self, parent, label: str, key: str, row: int, show: str | None = None) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = ttk.Entry(parent, textvariable=self.vars[key], show=show)
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5)

    def _path_entry(self, parent, label: str, key: str, row: int, command) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=self.vars[key]).grid(row=row, column=1, sticky="ew", pady=5)
        ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2, sticky="e", padx=(8, 0), pady=5)

    def _browse_download_dir(self) -> None:
        selected = filedialog.askdirectory(title="Pilih folder download")
        if selected:
            self.vars["download_dir"].set(selected)

    def _browse_chromedriver(self) -> None:
        selected = filedialog.askopenfilename(
            title="Pilih chromedriver.exe",
            filetypes=(("ChromeDriver", "chromedriver.exe"), ("Executable", "*.exe"), ("All files", "*.*")),
        )
        if selected:
            self.vars["chromedriver_path"].set(selected)

    def _setup_logging(self) -> None:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(TkLogHandler(self.root, self.log_text))

    def start_download(self) -> None:
        config = self._collect_config()
        missing = [label for key, label in (("nik", "NIK"), ("password", "Password"), ("target_period", "Periode")) if not config[key]]
        if missing:
            messagebox.showerror(APP_TITLE, "Field wajib belum diisi: " + ", ".join(missing))
            return

        save_config(config)
        self.start_button.configure(state="disabled")
        self.status_var.set("Berjalan. Selesaikan ALTCHA/login di Chrome jika diminta.")
        logging.info("Config disimpan ke %s", CONFIG_FILE)

        thread = threading.Thread(target=self._run_download, args=(config["target_period"],), daemon=True)
        thread.start()

    def _collect_config(self) -> dict:
        config = {**self.config_data}
        for key, variable in self.vars.items():
            config[key] = variable.get().strip()
        config["url"] = config.get("url") or DEFAULT_URL
        config["browser_headless"] = False
        config["selenium_timeout"] = int(config.get("selenium_timeout") or 20)
        config["captcha_retry"] = int(config.get("captcha_retry") or 5)
        return config

    def _run_download(self, target_period: str) -> None:
        try:
            from main import run_app

            exit_code = run_app(target_period=target_period, prompt_period=False, prompt_before_close=False)
            self.root.after(0, self._finish, exit_code)
        except Exception:
            logging.exception("Proses gagal.")
            self.root.after(0, self._finish, 1)

    def _finish(self, exit_code: int) -> None:
        self.start_button.configure(state="normal")
        if exit_code == 0:
            self.status_var.set("Selesai")
            messagebox.showinfo(APP_TITLE, "Proses selesai.")
        else:
            self.status_var.set("Gagal. Cek log proses.")
            messagebox.showerror(APP_TITLE, "Proses gagal. Cek log proses.")

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    CoretaxApp().run()
