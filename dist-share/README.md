# Withholding Slip Coretax

Tool ini dipakai untuk login ke Coretax DJP, mengganti tenant bila perlu, lalu mengunduh bukti potong PDF untuk periode yang dipilih.

## Cara pakai untuk user

1. Extract folder aplikasi.
2. Buka file `config.json`.
3. Isi `nik` dan `password`.
4. Pastikan `tenant_name` dan `tenant_npwp` sesuai.
5. Jalankan setup sekali:
   - Windows: `setup_windows.bat`
   - macOS: `setup_mac.command`
6. Setelah setup selesai, jalankan:
   - Windows: `run_windows.bat`
   - macOS: `run_mac.command`
7. Saat diminta, masukkan periode bulan.
8. Browser akan terbuka. Selesaikan ALTCHA dan klik login bila masih diminta.
9. Setelah login sukses, aplikasi lanjut otomatis ke proses download.

## File penting

- `config.json`: konfigurasi yang dipakai aplikasi.
- `config.template.json`: template jika ingin membuat ulang `config.json`.
- `run_windows.bat`: launcher untuk Windows.
- `run_mac.command`: launcher untuk macOS.
- `setup_windows.bat`: setup dependency untuk Windows.
- `setup_mac.command`: setup dependency untuk macOS.
- `.session/coretax_cookies.json`: session cookies lokal agar tidak login terus-menerus.

## Contoh `config.json`

```json
{
  "nik": "3515xxxxxxxxxxxx",
  "password": "isi_password_di_sini",
  "url": "https://coretaxdjp.pajak.go.id/identityproviderportal/Account/Login",
  "target_period": "Januari 2026",
  "tenant_name": "CYBERINDO MEGA PERSADA",
  "tenant_npwp": "0032779977063000",
  "download_dir": "",
  "chromedriver_path": "",
  "browser_headless": false,
  "selenium_timeout": 20,
  "captcha_retry": 5
}
```

## Keterangan field

- `nik`: NIK login Coretax.
- `password`: password login Coretax.
- `url`: URL halaman login.
- `target_period`: default periode bila user langsung tekan Enter saat prompt.
- `tenant_name`: nama tenant/perwakilan yang harus aktif setelah login.
- `tenant_npwp`: NPWP tenant/perwakilan yang harus aktif setelah login.
- `download_dir`: folder hasil download. Jika kosong, default ke `~/Downloads/CoretaxSlips`.
- `chromedriver_path`: opsional. Kosongkan jika ingin auto-detect.
- `browser_headless`: sebaiknya tetap `false` karena login butuh interaksi ALTCHA.
- `selenium_timeout`: timeout Selenium dalam detik.
- `captcha_retry`: saat ini hanya dipakai sebagai setting kompatibilitas.

## Perilaku aplikasi

- Mengisi username dan password otomatis.
- Mencoba memulihkan session cookies lama.
- Jika session masih valid, login bisa terlewati.
- Jika tenant aktif belum benar, aplikasi mencoba mengganti ke tenant target.
- Setelah sukses, session cookies disimpan lagi untuk run berikutnya.

## Catatan distribusi

- `config.json` berisi kredensial. Jangan commit ke repository publik.
- `run_mac.command` mungkin perlu izin execute sekali di macOS.
- Build tetap Python-based, jadi mesin tujuan harus punya Python 3.
- Jalankan setup sekali sebelum run pertama.

## Troubleshooting

- Jika `config.json` belum ada, salin `config.template.json` menjadi `config.json`.
- Jika muncul `No module named 'selenium'`, berarti setup belum dijalankan atau `venv` rusak. Jalankan `setup_mac.command` atau `setup_windows.bat`.
- Jika Chrome tidak terbuka, kosongkan `chromedriver_path` dulu.
- Jika tenant tidak terganti, cek `tenant_name` dan `tenant_npwp`.
- Jika login diminta lagi, kemungkinan session cookies sudah expired.
