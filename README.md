# Withholding Slip Coretax

Tool GUI untuk login ke Coretax DJP dan download bukti potong PDF berdasarkan periode.

## Untuk Build .exe

Build harus dilakukan dari Windows, bukan WSL, supaya hasilnya benar-benar file `.exe`.

Yang perlu ada di laptop build:

- Python 3 Windows dari python.org
- Opsi "Add Python to PATH" aktif saat install Python
- Google Chrome
- Internet untuk download dependency saat build pertama

Langkah build:

1. Extract source project ini di Windows.
2. Double click `build_windows.bat`.
3. Tunggu sampai muncul pesan build selesai.
4. Folder siap kirim ada di:

```text
finance-release\CoretaxSlip
```

Zip folder `CoretaxSlip` itu lalu kirim ke tim finance.

## Untuk Tim Finance

Finance tidak perlu install Python.

Yang perlu ada di komputer finance:

- Google Chrome

Cara pakai:

1. Extract folder `CoretaxSlip` yang dikirim.
2. Jalankan `CoretaxSlip.exe`.
3. Isi NIK, password, periode, tenant name, dan tenant NPWP di form aplikasi.
4. Klik `Mulai Download`.
5. Selesaikan ALTCHA/login di Chrome jika diminta.

Hasil PDF default tersimpan di:

```text
Downloads\CoretaxSlips
```

## File Penting

- `build_windows.bat`: dipakai developer/admin untuk membuat `.exe`.
- `config.template.json`: template konfigurasi.
- `config.json`: konfigurasi yang otomatis disimpan aplikasi setelah form diisi.
- `CoretaxSlip.exe`: aplikasi yang dijalankan finance.

## Field Opsional

- `Download Folder`: boleh dikosongkan. Jika kosong, hasil PDF masuk ke `Downloads\CoretaxSlips`.

## Catatan

- Jangan kirim/share `config.json` yang sudah berisi password.
- Jangan kirim source project ke finance; cukup kirim folder `finance-release\CoretaxSlip` hasil build.
- Jika build gagal karena `py` tidak dikenali, install ulang Python Windows dan centang "Add Python to PATH".
- Aplikasi tetap butuh Chrome karena login Coretax memakai browser.
