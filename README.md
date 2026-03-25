# Withholding Slip Coretax

Tool otomasi untuk login ke **Coretax DJP** dan mengunduh **Bukti Pemotongan (BP A1)** dalam format PDF menggunakan **Selenium**.  
Captcha dibaca otomatis memakai **Qwen VL OCR** melalui endpoint **DashScope API** yang kompatibel dengan OpenAI SDK.

---

## Demo

![Demo](public/demo.gif)

---

## Fitur

- Login otomatis ke portal Coretax
- Membaca captcha dengan OCR
- Navigasi ke menu **eBupot → Bukti Potong Saya**
- Filter slip berdasarkan periode
- Download PDF bukti potong otomatis
- Konfigurasi lewat file `.env`

---

## Struktur Project

```text
witholding-slip-coretax/
├── .env.example
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
├── core/
│   ├── __init__.py
│   └── settings.py
├── helpers/
│   ├── __init__.py
│   ├── env_utils.py
│   └── logger.py
├── public/
│   └── demo.gif
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── captcha_service.py
│   ├── download_service.py
│   └── navigation_service.py
└── utils/
    ├── __init__.py
    └── driver_utils.py
```

---

## Kebutuhan

Sebelum menjalankan project ini, pastikan tersedia:

| Kebutuhan | Wajib | Keterangan |
| --- | --- | --- |
| Python 3.11+ | Ya | Untuk menjalankan aplikasi |
| Google Chrome | Ya | Browser yang dipakai Selenium |
| ChromeDriver | Ya | Versinya harus cocok dengan versi Google Chrome |
| DashScope / Qwen API Key | Ya | Untuk OCR captcha |
| Koneksi internet | Ya | Dibutuhkan untuk login Coretax dan request OCR |

---

## Dependency Python

Dependency yang dipakai:

```txt
selenium>=4.18.0
pillow>=10.0.0
openai>=1.0.0
python-dotenv>=1.0.0
```

Install dengan:

```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan

### 1. Clone repository

```bash
git clone <repository-url>
cd witholding-slip-coretax
```

### 2. Buat virtual environment

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**

```bat
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

### 4. Buat file `.env`

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

### 5. Isi konfigurasi `.env`

Contoh:

```env
CORETAX_NIK=3515080312020003
CORETAX_PASSWORD=passwordkamu
CORETAX_TARGET_PERIOD=Januari 2026
CHROMEDRIVER_PATH=C:\tools\chromedriver.exe
QWEN_APIKEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 6. Jalankan aplikasi

```bash
python main.py
```

---

## Environment Variables

| Variable | Wajib | Default | Keterangan |
| --- | --- | --- | --- |
| `CORETAX_NIK` | Ya | - | NIK untuk login |
| `CORETAX_PASSWORD` | Ya | - | Password akun Coretax |
| `QWEN_APIKEY` | Ya | - | API key DashScope / Qwen |
| `CORETAX_TARGET_PERIOD` | Tidak | `Januari 2026` | Periode slip yang dicari |
| `CORETAX_URL` | Tidak | `https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login` | URL login Coretax |
| `CORETAX_DOWNLOAD_DIR` | Tidak | `~/Downloads/CoretaxSlips` | Folder hasil download PDF |
| `CHROMEDRIVER_PATH` | Tidak | `C:\tools\chromedriver.exe` | Lokasi file chromedriver |
| `BROWSER_HEADLESS` | Tidak | `false` | `true` untuk menjalankan Chrome tanpa tampilan |
| `SELENIUM_TIMEOUT` | Tidak | `20` | Timeout Selenium dalam detik |
| `CAPTCHA_RETRY` | Tidak | `5` | Jumlah maksimum retry login |
| `DASHSCOPE_BASE_URL` | Tidak | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | Base URL API DashScope |
| `DASHSCOPE_MODEL` | Tidak | `qwen3-vl-flash-2026-01-22` | Model OCR yang digunakan |

---

## Contoh `.env.example`

```env
# Coretax
CORETAX_NIK=your_nik_here
CORETAX_PASSWORD=your_password_here
CORETAX_TARGET_PERIOD=Januari 2026
CORETAX_URL=https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login
CORETAX_DOWNLOAD_DIR=

# ChromeDriver
# Windows : C:\tools\chromedriver.exe
# Linux   : /usr/bin/chromedriver
# Mac     : /usr/local/bin/chromedriver
CHROMEDRIVER_PATH=C:\tools\chromedriver.exe

# Selenium
BROWSER_HEADLESS=false
SELENIUM_TIMEOUT=20
CAPTCHA_RETRY=5

# Qwen / DashScope OCR
QWEN_APIKEY=your_qwen_apikey_here
DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
DASHSCOPE_MODEL=qwen3-vl-flash-2026-01-22
```

---

## Cara Kerja Singkat

Saat dijalankan, aplikasi akan:

1. Membaca konfigurasi dari `.env`
2. Membuka Chrome via Selenium
3. Masuk ke halaman login Coretax
4. Mengirim captcha ke OCR Qwen
5. Login ke akun Coretax
6. Navigasi ke halaman **Bukti Potong Saya**
7. Memfilter data dan mendownload file PDF yang cocok dengan periode target
8. Menunggu sampai download selesai

---

## Catatan Penting

- Project ini saat ini difokuskan untuk **download BP A1**
- Selector Selenium bisa berubah jika tampilan website Coretax berubah
- Hasil OCR captcha tidak selalu 100% akurat
- Aplikasi akan membuat folder download otomatis bila belum ada
- Setelah proses selesai, program menunggu input:

```text
Tekan Enter untuk menutup browser...
```

Jadi browser tidak langsung tertutup sampai kamu menekan Enter.

---

## Troubleshooting

### 1. Chrome gagal dibuka

Biasanya karena `CHROMEDRIVER_PATH` salah atau file chromedriver tidak cocok dengan versi Chrome.

Cek:

- path chromedriver benar
- chromedriver bisa dieksekusi
- versi Chrome dan ChromeDriver cocok

### 2. Login gagal terus

Kemungkinan:

- NIK atau password salah
- captcha terbaca salah
- selector halaman login berubah

### 3. Captcha sering salah

Coba:

- ulangi proses
- gunakan model OCR yang lebih besar
- pastikan gambar captcha memang muncul normal di browser

### 4. File tidak terdownload

Kemungkinan:

- tidak ada data pada periode tersebut
- tombol download berubah
- folder download tidak bisa diakses

### 5. Error API Qwen / DashScope

Periksa:

- `QWEN_APIKEY` valid
- `DASHSCOPE_BASE_URL` benar
- koneksi internet tersedia

---

## Keamanan

- **Jangan commit file `.env`**
- Jangan simpan kredensial asli di repository publik
- Pastikan `.env` sudah masuk `.gitignore`

---

## Limitasi

- Belum ada test otomatis
- Belum ada mekanisme fallback jika selector berubah drastis
- Belum ada support multi-browser
- Flow masih bergantung pada struktur UI Coretax saat ini

---

## Publish ke GitHub

```bash
git init
git add .
git commit -m "Initial clean project structure"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

---

## Saran Pengembangan Lanjutan

- Tambahkan logging yang lebih detail
- Tambahkan retry khusus untuk download
- Tambahkan validasi versi ChromeDriver
- Tambahkan mode batch untuk banyak periode
- Tambahkan unit test dan integration test
