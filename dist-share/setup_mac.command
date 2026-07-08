#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

rm -rf venv
python3 -m venv venv || exit 1
"venv/bin/python3" -m pip install --upgrade pip || exit 1
"venv/bin/python3" -m pip install -r requirements.txt || exit 1

echo ""
echo "Setup selesai."
echo "Selanjutnya jalankan run_mac.command"
read "?Tekan Enter untuk menutup jendela..."
